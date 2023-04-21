# Import
import uuid 
from datetime import datetime 

# Django Import
from django.db import models
from django.contrib.auth import get_user_model
from easy_thumbnails.fields import ThumbnailerImageField
from django.utils.translation import gettext  as _
from django.urls import reverse



# This method will return the currently active user model
User = get_user_model()


# Create your models here.
class Circle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    photo = ThumbnailerImageField(upload_to="circle_photos",blank = True)



    # The verbose_name_plural is a human readable name you give to the objects
    class Meta:
        verbose_name_plural = _("circles")

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("circle-detail", kwargs={"pk": self.pk})

    @property
    def ConfidentialRooms(self):
        # Return a list of user who are from this circle.
        ConfidentialRooms = User.objects.filter(ConfidentialRooms_through__circle = self)

        return ConfidentialRooms

    
    @property
    def organizers(self):
        # Return a list of users who are organizers of this circle.
        organizers = User.objects.filter(
            ConfidentialRooms_through__circle = self,
            ConfidentialRooms_through__is_organizer = True,
        )

        return organizers


    @property
    def upcoming_activities(self):
        """Return a list of activities that happen today or later."""
        today = datetime.today()

        return self.activities.filter(activity_date__gte=today)



    @property
    def annotated_ConfidentialRooms(self):
        # Return a ConfidentialRoom list annotated with activity count for current person

        annotated_ConfidentialRooms = []

        for member in self.ConfidentialRooms_through.all():
            member.activity_count = member.get_activity_count(circle=self)

            annotated_ConfidentialRooms.append(member)

        return annotated_ConfidentialRooms

    
    @property
    def ConfidentialRoom_score(self):
        # Number of times a person participated in a room

        return User.objects.filter(activities__circle=self).count()

    

    @property
    def pending_join_requests(self):
        # Get the join request who have not been approved or rejected
        return self.join_requests.filter(status = "PENDING")



class ConfidentialRoom(models.Model):
    circle = models.ForeignKey(Circle, related_name="ConfidentialRooms_through",on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, related_name="ConfidentialRooms_through" , on_delete=models.CASCADE)
    is_organizer = models.BooleanField(default=False)



    def __str__(self):
        return self.user.display_name


    def get_activity_count(self, circle=None):
        # Return a count of activities between the user and circle
        return self.user.get_activity_count(circle= self.circle)


    class Meta:
        unique_together = (
            "circle",
            "user",
        )



class JoinRequest(models.Model):

    class JoinRequestStatusChoices(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        APPROVED = "APPROVED", _("Approved")
        REJECTED = "REJECTED", _("Rejected")

    
    circle = models.ForeignKey(Circle, related_name="join_requests", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="join_requests" , on_delete=models.CASCADE)
    status = models.CharField(
        max_length=50,
        choices=JoinRequestStatusChoices.choices,
        default=JoinRequestStatusChoices.PENDING,)
    

    