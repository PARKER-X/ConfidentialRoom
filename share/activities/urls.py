from django.urls import path
from . import views
from .views import ActivityCreateView

urlpatterns = [
    path('', views.activities, name="activities"),
    path("create",ActivityCreateView.as_view(),name="activity-create"),
]

