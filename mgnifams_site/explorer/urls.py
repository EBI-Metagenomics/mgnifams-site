from django.urls import path
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('details/', views.details, name='details'),
    path('mgnifam_names/', views.mgnifam_names, name='mgnifam_names'),
]
