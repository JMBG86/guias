from django.urls import path
from . import views

urlpatterns = [
    path('clinicas/', views.clinica_list, name='clinica_list'),
    path('clinicas/add/', views.clinica_add, name='clinica_add'),
    path('clinicas/delete/<int:pk>/', views.clinica_delete, name='clinica_delete'),
    path('guias/overview/', views.overview_guides, name='overview_guides'),
    path('guias/create/', views.guia_create, name='guia_create'),
    path('guias/delete/<int:pk>/', views.guia_delete, name='guia_delete'),
    path('guias/pdf/', views.guia_pdf, name='guia_pdf'),
    
    path('guias/close_monthly/', views.guia_close_monthly, name='guia_close_monthly'),
    path('', views.home, name='home'), # Default view
]