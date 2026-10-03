import json
from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import models

from .git_sync import push_files
from .images import crop_to_ratio


class GalleryItem(models.Model):
    GENRE_CHOICES = [
        ("crea", "Crea"),
        ("musical", "Musical"),
        ("rekenen", "Rekenen"),
        ("spelling", "Spelling"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="main/images/")
    tiktok_url = models.URLField(max_length=500, blank=True)
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default="crea")
    order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers show first. Leave at 0 to put a new item at the top.",
    )
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "-id"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        new_upload = bool(self.image) and not self.image._committed
        if new_upload:
            cropped = crop_to_ratio(self.image)
            if cropped:
                self.image.save(Path(self.image.name).name, cropped, save=False)
        super().save(*args, **kwargs)
        if new_upload:
            push_files([self.image.path], f"Afbeelding toegevoegd: {self.title}")

    @property
    def files_json(self):
        return json.dumps([{"url": f.url} for f in self.files.all()])


class GalleryFile(models.Model):
    item = models.ForeignKey(GalleryItem, related_name="files", on_delete=models.CASCADE)
    file = models.FileField(upload_to="main/files/", blank=True)
    external_url = models.URLField(
        max_length=500, blank=True, help_text="Use this instead of uploading, e.g. a YouTube link."
    )

    def clean(self):
        if bool(self.file) == bool(self.external_url):
            raise ValidationError("Upload a file or enter a link (not both).")

    def save(self, *args, **kwargs):
        new_upload = bool(self.file) and not self.file._committed
        super().save(*args, **kwargs)
        if new_upload:
            push_files([self.file.path], f"Bestand toegevoegd: {self.file.name} ({self.item.title})")

    @property
    def url(self):
        return self.file.url if self.file else self.external_url

    def __str__(self):
        return self.url
