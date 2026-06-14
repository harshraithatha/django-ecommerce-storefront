import os
import shutil

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.store.models import Product, ProductImage


class Command(BaseCommand):
    help = (
        'Move existing product media out of the flat media/uploads/ folder into '
        'the structured products/<slug>/ layout, regenerate thumbnails, and '
        'remove the now-orphaned files.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would change without touching any files.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        migrated = 0

        for product in Product.objects.all():
            if product.image and not self._already_organized(product.image.name):
                ext = os.path.splitext(product.image.name)[1].lower() or '.jpg'
                target = '%s%s' % (product.slug, ext)
                self.stdout.write('Product "%s": %s -> products/%s/original/%s'
                                  % (product, product.image.name, product.slug, target))

                if not dry_run:
                    content = self._read(product.image)
                    # save=False so the field is re-keyed and the thumbnail is
                    # regenerated together in a single Product.save() below.
                    product.image.save(target, ContentFile(content), save=False)
                    product.save()
                migrated += 1

            for index, gallery in enumerate(product.images.all(), start=1):
                if not gallery.image or self._already_organized(gallery.image.name):
                    continue

                ext = os.path.splitext(gallery.image.name)[1].lower() or '.jpg'
                target = '%s-%s%s' % (product.slug, index, ext)
                self.stdout.write('  Gallery #%s: %s -> products/%s/gallery/original/%s'
                                  % (index, gallery.image.name, product.slug, target))

                if not dry_run:
                    content = self._read(gallery.image)
                    gallery.image.save(target, ContentFile(content), save=False)
                    gallery.save()
                migrated += 1

        self._cleanup_uploads(dry_run)

        verb = 'Would migrate' if dry_run else 'Migrated'
        self.stdout.write(self.style.SUCCESS('%s %s image(s).' % (verb, migrated)))

    def _already_organized(self, name):
        return name.startswith('products/')

    def _read(self, fieldfile):
        fieldfile.open('rb')
        try:
            return fieldfile.read()
        finally:
            fieldfile.close()

    def _cleanup_uploads(self, dry_run):
        """Remove the legacy media/uploads/ tree.

        After migration nothing in the database references it (the only other
        image fields in the project upload to media/site/).
        """
        uploads_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        if not os.path.isdir(uploads_dir):
            return

        leftover = sum(len(files) for _, _, files in os.walk(uploads_dir))
        self.stdout.write('Removing legacy media/uploads/ (%s orphaned file(s))' % leftover)

        if not dry_run:
            shutil.rmtree(uploads_dir)
