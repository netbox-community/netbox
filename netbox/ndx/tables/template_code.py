CATALOG_ENTRY_LINK = """
<a href="{% url 'ndx:catalog_entry' vendor_slug=record.vendor_slug slug=record.slug %}">{{ value }}</a>
"""

CATALOG_SOURCE = """
{% if value == 'netbox_labs' or value == 'both' %}
  <span class="badge text-bg-green" title="NetBox Labs">NBL</span>
{% endif %}
{% if value != 'netbox_labs' %}
  <span class="badge text-bg-gray" title="Community">DTL</span>
{% endif %}
"""

CATALOG_ENRICHMENT = """
{% for flag, enabled in record.enrichment_flags.items %}
  {% if enabled %}<span class="badge text-bg-blue">{{ flag }}</span>{% endif %}
{% endfor %}
"""

CATALOG_IMPORTED = """
{% if record.import_record %}
  <a href="{{ record.import_record.get_absolute_url }}">
    <i class="mdi mdi-check-bold text-success"></i>
    {% if record.import_record.update_available %}<span class="badge text-bg-warning">Update available</span>{% endif %}
  </a>
{% endif %}
"""

PROVENANCE_SOURCE = """
{% if value|slice:":8" == "https://" or value|slice:":7" == "http://" %}
  <a href="{{ value }}" target="_blank" rel="noopener noreferrer">{{ value }}</a>
{% else %}
  {{ value|placeholder }}
{% endif %}
"""
