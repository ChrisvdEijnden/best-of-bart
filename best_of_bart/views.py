from collections import Counter

from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
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
    items = list(visible_items())
    counts = Counter(item.genre for item in items)
    filters = [
        {'value': value, 'label': label, 'count': counts[value]}
        for value, label in GalleryItem.GENRE_CHOICES
        if counts[value]
    ]
    # ?genre=rekenen is rendered server-side, so a shared or refreshed
    # filtered link opens already filtered, with no flash of all items.
    active_genre = request.GET.get('genre')
    if active_genre not in counts:
        active_genre = 'all'
    return render(request, 'items.html', {
        'gallery_items': items,
        'filters': filters,
        'active_genre': active_genre,
        'total_items': len(items),
    })


def lesson_view(request, pk, slug=None):
    """A lesson's own page: what a shared link, a refresh or a search engine
    gets. On the gallery the same URL opens the lesson in the popup instead."""
    item = get_object_or_404(visible_items(), pk=pk)
    if slug != item.slug:
        return redirect(item, permanent=True)
    return render(request, 'lesson.html', {
        'item': item,
        'image_url': settings.SITE_URL + item.thumbnail_url,
        'page_url': settings.SITE_URL + item.get_absolute_url(),
    })


def contact_view(request):
    return render(request, 'contact.html')
