from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='petitions.index'),
    path('create/', views.create, name='petitions.create'),
    path('<int:id>/vote/', views.vote, name='petitions.vote'),
    path('<int:id>/dislike/', views.dislike, name='petitions.dislike'),
]