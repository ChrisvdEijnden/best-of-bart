from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('items/', views.items_view, name='items'),
    path('', views.home_view, name='home'),
    path('contact/', views.contact_view, name='contact'),
]

urlpatterns += [
    path(
        "ads.txt",
        RedirectView.as_view(
            url=staticfiles_storage.url("ads.txt"),
            permanent=True,
        ),
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)