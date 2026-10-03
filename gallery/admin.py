from django.contrib import admin
from django.utils.html import format_html

from .models import GalleryFile, GalleryItem


class GalleryFileInline(admin.TabularInline):
    model = GalleryFile
    extra = 1


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "title", "genre", "order", "is_visible")
    list_display_links = ("thumbnail", "title")
    list_editable = ("order", "is_visible")
    list_filter = ("genre", "is_visible")
    search_fields = ("title", "description")
    inlines = [GalleryFileInline]

    @admin.display(description="Image")
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:60px;border-radius:4px">', obj.image.url)
        return "—"
