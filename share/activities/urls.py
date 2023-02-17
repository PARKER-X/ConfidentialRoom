from django.urls import path
from . import views
from .views import ActivityCreateView, ActivityUpdateView, ActivitySetDoneView, ActivityAddParticipantView,ActivityRemoveParticipantView,ActivityDeleteView

urlpatterns = [
    path('', views.activities, name="activities"),
    path("create",ActivityCreateView.as_view(),name="activity-create"),
    path("update/<slug:pk>/", ActivityUpdateView.as_view(),name="activity-update"),
    path("update/<slug:activity_id>/set_done",ActivitySetDoneView.as_view(), name="activity-set-done",),
    path("update/<slug:activity_id>/add_participant" ,ActivityAddParticipantView.as_view(), name="activity-add-participant",),
    path("update/<slug:activity_id>/remove_participant",ActivityRemoveParticipantView.as_view(),name="activity-remove-participant",),
    path("delete/<slug:activity_id>/",ActivityDeleteView.as_view(),name="activity-delete",),
]

