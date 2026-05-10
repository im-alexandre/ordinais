"""URLs da API REST do Electre MOR."""

from rest_framework.routers import DefaultRouter

from core.api.views import ProjectViewSet

app_name = "api"

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project")

urlpatterns = router.urls
