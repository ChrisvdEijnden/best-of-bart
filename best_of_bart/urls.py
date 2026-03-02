from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('items/', views.items_view, name='items'),
    path('', views.home_view, name='home'),
    path('contact/', views.contact_view, name='contact'),
    path('ads.txt', views.ads_txt, name='ads_txt'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
