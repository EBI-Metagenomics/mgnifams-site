from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('statistics/', views.statistics, name='statistics'),
    path('mgnifams_list/', views.mgnifams_list, name='mgnifams_list'),
    path('mgnifams_data/', views.mgnifams_data, name='mgnifams_data'),
    path('details/<str:pk>/', views.details, name='details'),
    path('serve_blob/<int:pk>/<str:column_name>/', views.serve_blob_as_file, name='serve_blob_as_file'),
]
