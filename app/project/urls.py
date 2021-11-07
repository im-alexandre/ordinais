"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from app import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('form_projeto/', views.projeto_form, name='projeto_form'),
    path('form/', views.form, name='form'),
    path('salva_projeto/', views.salva_projeto, name='salva_projeto'),
    path('salva_criterios_alternativas/',
         views.salva_criterios_alternativas,
         name='salva_criterios_alternativas'),
    path('avalia/', views.avalia, name='avalia'),
    path('resultado/', views.resultado, name='resultado'),
    path('relatorio/', views.relatorio, name='relatorio'),
]
