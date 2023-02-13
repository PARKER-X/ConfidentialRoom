from django.urls import path


from .views import (
    CircleCreateView
)


urlpatterns = [
    path("create",CircleCreateView.as_view(),name="circle-create",),
    
]
