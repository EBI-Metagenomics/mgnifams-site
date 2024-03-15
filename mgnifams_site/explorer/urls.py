from django.urls import path
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('details/', views.details, name='details'),
    path('khalifam_names/', views.khalifam_names, name='khalifam_names'),
]
