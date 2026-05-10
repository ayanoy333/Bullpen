from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('list/', views.pitcher_list, name='pitcher_list'),
    path('calc/', views.calculator, name='calculator'),
    path('edit/<int:pk>/', views.pitcher_edit, name='pitcher_edit'),
    path('toggle_favorite/<int:pk>/', views.toggle_favorite, name='toggle_favorite'),
]