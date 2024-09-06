from django.urls import path
from apps.projects.views.project_views import ProjectsListAPIView


urlpatterns = [
    path('', ProjectsListAPIView.as_view()),
]
