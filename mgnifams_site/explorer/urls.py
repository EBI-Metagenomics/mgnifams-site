from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('details/', views.details, name='details'),
    path('serve_blob/<int:pk>/<str:column_name>/', views.serve_blob_as_file, name='serve_blob_as_file'),
    path('submit_hmmsearch/<int:mgyf_id>/', views.submit_hmmsearch, name='submit_hmmsearch'),
]
