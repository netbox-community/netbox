
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models

from utilities.models import CreatedUpdatedModel

import time

from django.db.models.signals import pre_delete
from django.dispatch import receiver

import ipam.models


class Zone(CreatedUpdatedModel):
    """
    A Zone represents a DNS zone. It contains SOA data but no records, records are represented as Record objects.
    """
    name = models.CharField(max_length=100)
    ttl = models.PositiveIntegerField()
    soa_name = models.CharField(max_length=100)
    soa_contact = models.CharField(max_length=100)

    soa_serial = models.CharField(max_length=10)
    bind_changed = models.BooleanField(default=True)

    soa_refresh = models.PositiveIntegerField()
    soa_retry = models.PositiveIntegerField()
    soa_expire = models.PositiveIntegerField()
    soa_minimum = models.PositiveIntegerField()
    extra_conf = models.CharField(max_length=500, blank=True)
    description = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dns:zone', args=[self.pk])

    def save(self, *args, **kwargs):
        self.bind_changed = True
        super(Zone, self).save(*args, **kwargs)

    def set_bind_changed(self, value):
        self.bind_changed = value
        super(Zone, self).save()

    def update_serial(self):
        """
        Each time a record or the zone is modified, the serial is incremented.
        """
        current_date = time.strftime('%Y%m%d', time.localtime())
        if not self.soa_serial:
            self.soa_serial = current_date + '01'
        else:
            serial_date = self.soa_serial[:8]
            serial_num = self.soa_serial[8:]

            if serial_date != current_date:
                self.soa_serial = current_date + '01'
            else:
                serial_num = int(serial_num)
                serial_num += 1
                if serial_num < 10:
                    self.soa_serial = current_date + '0' + str(serial_num)
                else:
                    self.soa_serial = current_date + str(serial_num)
        self.set_bind_changed(False)

    def to_csv(self):
        return ','.join([
            self.name,
            str(self.ttl),
            self.soa_name,
            self.soa_contact,
            self.soa_serial,
            str(self.soa_refresh),
            str(self.soa_retry),
            str(self.soa_expire),
            str(self.soa_minimum),
            '"{}"'.format(self.extra_conf) if self.extra_conf else '',
            self.description,
        ])

    def to_bind(self, records):
        if self.bind_changed:
            self.update_serial()
        bind_records = ''
        for r in records:
            bind_records += r.to_bind() + '\n'
        bind_export = '\n'.join([
            '; ' + self.name + ((' (' + self.description + ')') if self.description else ''),
            '; gen by netbox ( ' + time.strftime('%A %B %d %Y %H:%M:%S', time.localtime()) + ' ) ',
            '',
            '$TTL ' + str(self.ttl),
            self.soa_name.ljust(30) + '    IN    ' + 'SOA                   ' + self.soa_contact + ' (',
            '    ' + self.soa_serial.ljust(30) + ' ; serial',
            '    ' + str(self.soa_refresh).ljust(30) + ' ; refresh',
            '    ' + str(self.soa_retry).ljust(30) + ' ; retry',
            '    ' + str(self.soa_expire).ljust(30) + ' ; expire',
            '    ' + str(self.soa_minimum).ljust(29) + ') ; minimum',
            '',
            '',
            '',
        ])
        bind_export += '\n' + bind_records
        bind_export += '\n' + '; end '
        return bind_export


class Record(CreatedUpdatedModel):
    """
    A Record represents a DNS record, i.e. a row in a DNS zone.
    """
    name = models.CharField(max_length=100)
    record_type = models.CharField(max_length=10)
    priority = models.PositiveIntegerField(blank=True, null=True)
    zone = models.ForeignKey('Zone', related_name='records', on_delete=models.CASCADE)
    address = models.ForeignKey('ipam.IPAddress', related_name='records', on_delete=models.PROTECT, blank=True, null=True)
    value = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dns:record', args=[self.pk])

    def clean(self):
        self.record_type = self.record_type.upper()
        if not self.address and not self.value:
            raise ValidationError("DNS records must have either an IP address or a text value")

    def save(self, *args, **kwargs):
        self.zone.save()  # in order to update serial.
        super(Record, self).save(*args, **kwargs)

    def to_csv(self):
        return ','.join([
            self.zone.name,
            self.name,
            self.record_type,
            str(self.priority) if self.priority else '',
            str(self.address) if self.address else '',
            self.value,
            self.description,
        ])

    def to_bind(self):
        return ''.join([
            (self.name if self.name != '@' else '').ljust(30),
            '    IN    ',
            self.record_type.upper().ljust(10),
            '    ',
            (str(self.priority) if self.priority else '').ljust(4),
            '    ',
            (str(self.address).split('/')[0] if self.address else self.value).ljust(25),
            '  ',
            ' ; ' + self.description + ' ; gen by netbox ( ' + time.strftime('%A %B %d %Y %H:%M:%S', time.localtime()) + ' ) '
        ])


@receiver(pre_delete, sender=Record)
def on_record_delete(sender, **kwargs):
    kwargs['instance'].zone.save()


#
# BIND Exports
#


def export_bind_forward():
    zones = Zone.objects.all()

    zones_list = []
    for z in zones:
        records = Record.objects.filter(zone=z)
        zones_list.append({
            'num': len(zones_list),
            'id': z.name,
            'extra_conf': z.extra_conf,
            'content': z.to_bind(records)
        })

    return zones_list


def export_bind_reverse():
    zones = {}

    prefixes = ipam.models.Prefix.objects.all()

    for p in prefixes:
        child_ip = ipam.models.IPAddress.objects.filter(address__net_contained_or_equal=str(p.prefix))
        z = p.to_bind(child_ip)
        for zz in z:
            if not zz['id'] in zones:
                zones[zz['id']] = (zz['content'], p.extra_conf)

    zones_list = []
    for zid, zc in zones.items():
        zones_list.append({
            'num': len(zones_list),
            'id': zid,
            'content': zc[0],
            'extra_conf': zc[1],
        })

    return zones_list
