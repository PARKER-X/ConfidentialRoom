from django.urls import path


from .views import (
    CircleCreateView,
    CircleDetailView,
    CircleListView
)


urlpatterns = [
    path("", CircleListView.as_view(), name="circle-list"),
    path("create",CircleCreateView.as_view(),name="circle-create",),
    path("<slug:pk>/", CircleDetailView.as_view(), name="circle-detail"),

    
]
