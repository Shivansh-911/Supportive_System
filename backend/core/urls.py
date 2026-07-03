from django.urls import include, path

urlpatterns = [
    path("api/", include("orchestrator_agent.urls")),
]
