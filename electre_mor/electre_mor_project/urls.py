"""URL configuration for electre_mor_project."""

from django.contrib import admin
from django.urls import include, path

from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.landing_page, name="index"),
    path("api/v1/", include(("core.api.urls", "api"), namespace="v1")),
    path("project_setup/", views.index, name="projeto_form"),
    path("metodo/", views.metodo, name="metodo"),
    path("projeto/<projeto_id>/", views.projeto, name="projeto"),
    path("dm_criteria_alt/<projeto_id>/",
         views.cadastradecisores,
         name="cadastradecisores"),
    path("evaluate_criteria/<projeto_id>/",
         views.avaliarcriterios,
         name="avaliarcriterios"),
    path("evaluate_alt/<projeto_id>/",
         views.avaliaralternativas,
         name="avaliaralternativas"),
    path("result/<projeto_id>/", views.resultado, name="resultado"),
    path("deletarprojeto/<projeto_id>/",
         views.deletarprojeto,
         name="deletarprojeto"),
    path("download/<projeto_id>", views.download_file, name="download_file"),
    path("alt_criteria/<projeto_id>/",
         views.alternativacriterio,
         name="alternativacriterio"),
    path("partial_result_tresholds/<projeto_id>/",
         views.resultado_sapevo,
         name="resultadosapevo"),
]
