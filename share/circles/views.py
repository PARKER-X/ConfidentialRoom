# Django Import 
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic import DetailView, TemplateView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.core.paginator import Paginator



#  App Import
from .models import Circle, JoinRequest, ConfidentialRoom
from activities.forms import ActivityModelForm

# Create your views here.

class CircleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Circle
    fields = [
        "name",
        "photo",
    ]


    def get_form(self, form_class: None):
        form = super().get_form(form_class)
        form.fields["name"].widget.attrs.update({"autofocus":"autofocus"})

        return form

    def form_valid(self,form):
        circle = form.save()

        confidental = ConfidentialRoom(
            circle = Circle,
            user = self.request.user,
            is_organizer = True,
        )


        confidental.save()

        return HttpResponseRedirect(circle.get_absolute_url())

    
    def test_func(self):
        return  not self.request.user.is_care_circle_organizer


class CircleDetailView(LoginRequiredMixin,UserPassesTestMixin,DetailView):
    model = Circle
    context_object_name = 'circle'
    template_name = "circles/circle_detail.html"


    def test_func(self):
        circle = Circle.objects.get(id=self.kwargs["pk"])
        user = self.request.user
        user_can_access_circle = user in circle.ConfidentialRooms

        return user_can_access_circle


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.object.activities.all()
        paginator = Paginator(queryset,4)
        page = self.request.GET.get("page")



        # Invitation URL
        circle_id = context["circle"].id
        invitation_path = reverse("circle-join", kwargs={"circle-id":circle_id})
        invitation_url = self.request.build_absolute_uri(invitation_path)

        context["invitation_url"] = invitation_url
        context["add_activity_form"] = ActivityModelForm


        try:
            activities_page = paginator.page(page)
        except PageNotAnInteger:
            activities_page = paginator.page(1)
        except EmptyPage:
            activities_page = paginator.page(paginator.num_pages)

        context["activities_page"] = activities_page

        return context


    


class  CircleListView(ListView):
    model = Circle
    template_name = "circles/circle_list.html"



