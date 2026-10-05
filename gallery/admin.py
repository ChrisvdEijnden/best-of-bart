from django.contrib import admin
from django.db.models import Count
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.html import format_html

from . import git_sync
from .models import GalleryFile, GalleryItem

admin.site.site_header = "Best of Bart beheer"
admin.site.site_title = "Best of Bart"
admin.site.index_title = "Lessen beheren"
# /beheer/login/ uses the site's own styled login page.
admin.site.login_template = "admin.html"


class GalleryFileInline(admin.TabularInline):
    model = GalleryFile
    extra = 1


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "title", "genre", "file_count", "order", "is_visible")
    list_display_links = ("thumbnail", "title")
    list_editable = ("order", "is_visible")
    list_filter = ("genre", "is_visible")
    list_per_page = 50
    search_fields = ("title", "description")
    readonly_fields = ("preview",)
    fieldsets = (
        (None, {"fields": ("title", "genre", "description", "tiktok_url")}),
        ("Voorkant", {
            "fields": ("image", "preview"),
            "description": "De afbeelding wordt bij het uploaden automatisch bijgesneden tot 5:7 (staand).",
        }),
        ("Weergave", {"fields": ("order", "is_visible")}),
    )
    inlines = [GalleryFileInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(num_files=Count("files"))

    @admin.display(description="Image")
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:60px;border-radius:4px">', obj.image.url)
        return "—"

    @admin.display(description="Voorbeeld")
    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:150px;aspect-ratio:5/7;object-fit:cover;'
                'border:2px solid #333;border-radius:4px">',
                obj.image.url,
            )
        return "—"

    @admin.display(description="Bestanden", ordering="num_files")
    def file_count(self, obj):
        return obj.num_files

    def get_urls(self):
        return [
            path("overzicht/", self.admin_site.admin_view(self.overview_view), name="gallery_overview"),
        ] + super().get_urls()

    def overview_view(self, request):
        items = GalleryItem.objects.prefetch_related("files")
        genres = dict(GalleryItem.GENRE_CHOICES)
        context = {
            **self.admin_site.each_context(request),
            "title": "Overzicht lessen",
            "opts": self.model._meta,
            "items": items,
            "genre_counts": [
                (genres.get(row["genre"], row["genre"]), row["n"])
                for row in GalleryItem.objects.values("genre").annotate(n=Count("id")).order_by("genre")
            ],
            "hidden_count": items.filter(is_visible=False).count(),
            "without_files": [item for item in items if not item.files.all()],
            "sync_log": git_sync.recent_log(),
        }
        return TemplateResponse(request, "admin/gallery_overview.html", context)
