# certificates/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('list/', views.certificate_list, name='certificate_list'),
    path('download/<str:certificate_id>/', views.download_certificate, name='download_certificate'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
