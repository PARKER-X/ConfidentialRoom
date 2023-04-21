# Django Import 
from django.shortcuts import render,redirect
from django.views.generic.edit import CreateView,UpdateView
from django.views.generic import DetailView, TemplateView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect,Http404
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views import View
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.core.paginator import Paginator
from django.utils.translation import gettext as _



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


    def get_form(self, form_class= None):
        form = super().get_form(form_class)
        form.fields["name"].widget.attrs.update({"autofocus":"autofocus"})

        return form

    def form_valid(self,form):
        circle = form.save()

        confidental = ConfidentialRoom(
            circle = circle,
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
        invitation_path = reverse("circle-join", kwargs={"circle_id":circle_id})
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


    


class  CircleListView(LoginRequiredMixin, TemplateView):
    template_name = "circles/circle_list.html"



def join_as_confidential(request,circle_id):
    if request.user.is_authenticated:
        try:
            circle = Circle.objects.get(pk=circle_id)
        except Circle.DoesNotExist:
            message = _("Could not found circle at the requested url")
            raise Http404(message)
        

        # Redirect to circle page if user is already in confidential room
        if ConfidentialRoom.objects.filter(
            circle = circle_id,
            user = request.user,
        ).exists():
            return redirect(circle)
        

        # Show "request received" if user has already submitted a join request
        if JoinRequest.objects.filter(
            circle = circle_id,
            user = request.user,
        ).exists():
            return render(request,"circles/circle_join_received.html")

        # Handle Join Request
        if request.method == "POST":
            join_request = JoinRequest(
                circle=circle,
                user = request.user,
            )
            join_request.save()
            return render(request, "circles/circle_join_received.html")

        # Show join by default
        return render(request, "circles/circle_join.html")

    # Show login/register buttons by default
    return render(request, "circles/login_register.html") 




class JoinRequestUpdateView(View):
    def get(self, request,circle_id, join_request_id, *args, **kwargs):
        circle = Circle.objects.get(id=circle_id)

        # Only organizer can update join requests
        if request.user not in circle.organizers:
            raise PermissionDenied()
        else:
            join_request  =  JoinRequest.objects.get(id = join_request_id,circle=circle)

            join_request_status = request.GET["status"]


            # If approved
            if join_request_status == "APPROVED":
                confidentialRoom = ConfidentialRoom(circle=circle,user = join_request.user,)
                confidentialRoom.save()

            
            # Always delete the join reguest once they handled by organizer
            join_request.delete()


            return redirect(circle)



class CircleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Circle
    fields = [
        "name",
        "photo",
    ]

    def test_func(self,*args, **kwargs):
        # Only organizer has power to update the circle detail
        circle = Circle.objects.get(id =self.kwargs["pk"])
        user = self.request.user


        # Check user is organizer or not
        user_can_update_circle = user in circle.organizers

        return user_can_update_circle

    def get_form(self, form_class=None):
        form =  super().get_form(form_class)
        form.fields["name"].widget.attrs.update({"autofocus":"autofocus"})

        return form

    def form_valid(self,form):
        # Used to delete old photos and thumbnails
        circle = Circle.objects.get(id = self.kwargs["pk"])
        circle.photo.delete()
        circle = form.save()

        return HttpResponseRedirect(circle.get_absolute_url())


from django.shortcuts import get_object_or_404
def room(request, pk):
    room = get_object_or_404(Circle, pk=pk)
    websocket_url = request.get_host() + '/ws/circles/' + room.name + '/'
    error_message = ''
    return render(request, 'circles/chat.html', context={'room': room, 'error_message': error_message})
    