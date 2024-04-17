from django.urls import path
from . import views
from .views import serve_blob_as_file
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('details/', views.details, name='details'),
    path('mgnifam_names/', views.mgnifam_names, name='mgnifam_names'),
    path('serve_blob/<int:pk>/<str:column_name>/', serve_blob_as_file, name='serve_blob_as_file'),
]
