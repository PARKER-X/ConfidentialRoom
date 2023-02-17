from django.urls import path


from .views import (
    CircleCreateView,
    CircleDetailView,
    CircleListView,
    join_as_confidential,
    JoinRequestUpdateView,
    CircleUpdateView,
)


urlpatterns = [
    path("", CircleListView.as_view(), name="circle-list"),
    path("create",CircleCreateView.as_view(),name="circle-create",),
    path("<slug:pk>/", CircleDetailView.as_view(), name="circle-detail"),
    path("<slug:circle_id>/join/",join_as_confidential, name="circle-join"),
    path("<slug:circle_id>/join-request/<slug:join_request_id>/",JoinRequestUpdateView.as_view(),name="update-join-request",),
    path("<slug:pk>/update/",CircleUpdateView.as_view(),name="circle-update"),

    
]
