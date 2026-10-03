import json

from django.core.exceptions import ValidationError
from django.db import models


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

    @property
    def url(self):
        return self.file.url if self.file else self.external_url

    def __str__(self):
        return self.url
