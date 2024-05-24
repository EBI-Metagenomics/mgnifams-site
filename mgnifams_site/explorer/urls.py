from django.urls import path
from . import views
from .views import serve_blob_as_file

urlpatterns = [
    path('', views.index, name='index'),
    path('details/', views.details, name='details'),
    path('serve_blob/<int:pk>/<str:column_name>/', serve_blob_as_file, name='serve_blob_as_file'),
]
