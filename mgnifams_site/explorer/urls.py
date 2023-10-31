from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('details/', views.details, name='details'),
    path('cluster_reps/', views.cluster_reps, name='cluster_reps'),
    path('unannotated_ids/', views.unannotated_ids, name='unannotated_ids'),
    path('family_members/<str:protein_id>/', views.family_members, name='family_members'),
]
