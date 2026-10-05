from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from . import views

urlpatterns = [
    path('beheer/', admin.site.urls),
    path('beheer/login/', views.AdminView.as_view(), name='login'),
    path('lessen/', views.items_view, name='lessen'),
    path('', views.home_view, name='home'),
    path('contact/', views.contact_view, name='contact'),
    # Uploaded images and zips. static() only works with DEBUG = True, so serve
    # media explicitly; if the web server already serves /media/ it wins anyway.
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
