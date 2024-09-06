from django.urls import path
from apps.tasks.views.tag_views import TagListAPIView


urlpatterns = [
    path('tags/', TagListAPIView.as_view()),
]
