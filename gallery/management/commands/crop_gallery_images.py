from django.core.management.base import BaseCommand

from gallery.images import crop_to_ratio
from gallery.models import GalleryItem


class Command(BaseCommand):
    help = "Crop existing gallery cover images to 5:7, in place."

    def handle(self, *args, **options):
        for item in GalleryItem.objects.exclude(image=""):
            with item.image.open("rb") as f:
                cropped = crop_to_ratio(f)
            if not cropped:
                continue
            with item.image.storage.open(item.image.name, "wb") as out:
                out.write(cropped.read())
            self.stdout.write(self.style.SUCCESS(f"Cropped: {item.title}"))
