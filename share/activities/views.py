from django.shortcuts import render
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.http import HttpResponseRedirect


from .models import Activity
from circles.models import Circle
from .forms import ActivityModelForm


# Create your views here.
def activities(request):
    return render(request, 'activities/activities.html')


class ActivityCreateView(LoginRequiredMixin, UserPassesTestMixin,  CreateView):
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
    
