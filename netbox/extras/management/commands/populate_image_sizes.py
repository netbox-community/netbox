from django.core.management.base import BaseCommand

from extras.models import ImageAttachment

# Number of records to read and write per batch
BATCH_SIZE = 100


class Command(BaseCommand):
    help = "Populate the image_size field for ImageAttachments that predate it"

    def handle(self, *args, **options):
        verbosity = options['verbosity']

        # Only consider attachments whose size has not yet been cached. This is safe to re-run: rows whose file
        # was unreadable on a previous run remain NULL and will be retried.
        queryset = ImageAttachment.objects.filter(image_size__isnull=True)
        total = queryset.count()

        if not total:
            if verbosity:
                self.stdout.write(self.style.SUCCESS("No image attachments require updating."))
            return

        if verbosity:
            self.stdout.write(f"Populating image_size for {total} image attachment(s)...")

        updated = 0
        skipped = 0
        batch = []

        for processed, attachment in enumerate(queryset.iterator(chunk_size=BATCH_SIZE), start=1):
            # These rows have image_size=NULL, so the size property reads the file from storage (returning None if
            # it's inaccessible) rather than returning a cached value.
            size = attachment.size
            if size is None:
                # File is inaccessible; leave image_size NULL so a future run can retry.
                skipped += 1
            else:
                attachment.image_size = size
                batch.append(attachment)

            if len(batch) >= BATCH_SIZE:
                ImageAttachment.objects.bulk_update(batch, ['image_size'])
                updated += len(batch)
                batch = []

            # Reading each file's size may issue a request to the storage backend, so emit periodic progress
            # for large tables rather than going silent until completion.
            if verbosity and processed % BATCH_SIZE == 0:
                self.stdout.write(f"  Processed {processed}/{total}...")

        if batch:
            ImageAttachment.objects.bulk_update(batch, ['image_size'])
            updated += len(batch)

        if verbosity:
            self.stdout.write(self.style.SUCCESS(f"Updated {updated} image attachment(s)."))
            if skipped:
                self.stdout.write(self.style.WARNING(
                    f"Skipped {skipped} inaccessible file(s); re-run this command to retry them."
                ))
