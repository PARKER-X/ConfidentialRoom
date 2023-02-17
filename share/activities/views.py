from django.shortcuts import render,redirect
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic import UpdateView
from django.views.generic import View


from .models import Activity
from circles.models import Circle
from .forms import ActivityModelForm


# Create your views here.
def activities(request):
    return render(request, 'activities/activities.html')


class ActivityCreateView(LoginRequiredMixin, UserPassesTestMixin,  View):
    raise_exception = True

    def test_func(self):
        circle_id = self.request.POST.get("circle",None)

        if circle_id:
            circle = Circle.objects.get(id=circle_id)

            user_is_organizer = self.request.user in circle.organizers
            user_is_ConfidentialRoom = self.request.user in circle.ConfidentialRooms

            user_can_update_activity = user_is_ConfidentialRoom or user_is_organizer

            return user_can_update_activity
        return False
    
    def post(self, *args, **kwargs):
        form = ActivityModelForm(self.request.POST)

        if form.is_valid():
            activity = form.save()

            redirect_to = reverse("circle-detail",kwargs={"pk":activity.circle.id,},)

            return HttpResponseRedirect(redirect_to)
    


class ActivityUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self ,*args, **kwargs):
        circle_id = self.request.POST.get("circle",None)

        if circle_id:
            circle = Circle.objects.get(id=circle_id)
            user_is_organizer = self.request.user in circle.organizers
            user_is_ConfidentialRoom = self.request.user in circle.ConfidentialRooms
            user_can_update_activity = user_is_organizer or user_is_ConfidentialRoom

            return user_can_update_activity
        
        return False

    
    def post(self, *args, **kwargs):
        activity = Activity.objects.get(pk = kwargs["pk"])
        form = ActivityModelForm(
            self.request.POST,
            instance=activity,
        )

        if form.is_valid():
            activity = form.save()

            redirect_to = reverse(
                "circle-detail",
                kwargs={
                    "pk":activity.circle.id
                },
            )
        
            return HttpResponseRedirect(redirect_to)


class ActivitySetDoneView(LoginRequiredMixin, UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        
        self.activity = Activity.objects.get(id = self.kwargs["activity_id"])
        user_is_participant = self.request.user in self.activity.participants.all()
        user_is_organizer = self.request.user in self.activity.circle.organizers


        user_can_update_activity = user_is_participant or user_is_organizer
        return user_can_update_activity

    def get(self, request, activity_id, *args, **kwargs):
        self.activity.done = True
        self.activity.save()

        return redirect(
            reverse(
                "circle-detail",
                kwargs={"pk":self.activity.circle.id},
            )
        )




class ActivityAddParticipantView(UserPassesTestMixin, LoginRequiredMixin, View):
    raise_exception = True

    def test_func(self, *args, **kwargs):
        """
        Only the circle's care organizers can add other companions to activity.
        Only the circle's companions can add themselves to an activity.
        """

        activity_id = self.kwargs.get("activity_id", None)

        if activity_id:
            activity = Activity.objects.get(id=activity_id)

            user_is_organizer = self.request.user in activity.circle.organizers
            user_is_ConfidentialRoom = self.request.user in activity.circle.ConfidentialRooms

            user_id = self.request.POST.get("user_id", None)
            user_is_adding_self = user_id == str(self.request.user.id)

            user_can_add_participant = user_is_organizer or (
               user_is_ConfidentialRoom  and user_is_adding_self
            )

            return user_can_add_participant

    def post(self, request, activity_id, *args, **kwargs):
        user_id = request.POST["user_id"]
        activity = Activity.objects.get(id=activity_id)

        activity.participants.add(user_id)

        return redirect(
            reverse(
                "circle-detail",
                kwargs={"pk": activity.circle.id},
            )
        )



class ActivityRemoveParticipantView(LoginRequiredMixin, UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self, *args, **kwargs):
        
        activity_id = self.kwargs.get("activity_id", None)

        if activity_id:
            activity = Activity.objects.get(id=activity_id)

            user_is_not_ConfidentialRooms = self.request.user not in activity.circle.ConfidentialRooms

            if user_is_not_ConfidentialRooms:
                return False

            user_is_organizer = self.request.user in activity.circle.organizers

            user_id = self.request.POST.get("user_id", None)
            user_is_removing_self = user_id == str(self.request.user.id)

            user_can_remove_participant = user_is_organizer or user_is_removing_self

            return user_can_remove_participant

    def post(self, request, activity_id, *args, **kwargs):
        user_id = request.POST["user_id"]
        activity = Activity.objects.get(id=activity_id)

        activity.participants.remove(user_id)

        return redirect(
            reverse(
                "circle-detail",
                kwargs={"pk": activity.circle.id},
            )
        )



class ActivityDeleteView(UserPassesTestMixin, LoginRequiredMixin, View):
    raise_exception = True

    def test_func(self, *args, **kwargs):
        """Only the circle's care organizers can delete activity"""
        self.activity = Activity.objects.get(id=self.kwargs["activity_id"])

        user_is_organizer = self.request.user in self.activity.circle.organizers

        user_can_delete_activity = user_is_organizer

        return user_can_delete_activity

    def post(self, request, *args, **kwargs):
        circle_id = self.activity.circle.id
        self.activity.delete()

        return redirect(
            reverse(
                "circle-detail",
                kwargs={"pk": circle_id},
            )
        )
