from django.shortcuts import render
from gallery.models import GalleryItem


def visible_items():
    return GalleryItem.objects.filter(is_visible=True).prefetch_related("files")


def home_view(request):
    items = visible_items()
    return render(request, 'home.html', {
        'gallery_items': items[:4],
        'total_items': items.count(),
    })


def items_view(request):
    return render(request, 'items.html', {
        'gallery_items': visible_items(),
    })


def contact_view(request):
    return render(request, 'contact.html')
