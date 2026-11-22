from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from . import views

urlpatterns = [
    path('beheer/', admin.site.urls),
    path('lessen/', views.items_view, name='lessen'),
    path('lessen/<int:pk>-<slug:slug>/', views.lesson_view, name='lesson'),
    path('lessen/<int:pk>/', views.lesson_view),
    path('', views.home_view, name='home'),
    path('contact/', views.contact_view, name='contact'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
