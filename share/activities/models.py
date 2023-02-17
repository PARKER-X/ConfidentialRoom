# import modules
from enum import Enum
import datetime



# Django imports
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse



from circles.models import Circle


User = get_user_model()



# Create your models here.
class Activity(models.Model):
    class ActivityTypeIcons(Enum):
        PARTY = "bi-party"
        CALL = "bi-call"
        NATURE = "bi-tree"
        SHOPPING = "bi-cart"
        ENTERTAINMENT = "bi-entertainment"

    
    class ActivityTypeChoices(models.TextChoices):
        PARTY =  "PARTY", _("Party")
        CALL = "CALL", _("Call")
        NATURE = "NATURE", _("Nature")
        SHOPPING = "SHOPPING", _("Shopping")
        ENTERTAINMENT = "ENTERTAINMENT", _("Entertainment")

    activity_type = models.CharField(
        max_length=50,
        choices=ActivityTypeChoices.choices,
        default=ActivityTypeChoices.PARTY
)

    activity_date = models.DateField(default=datetime.date.today)


    note = models.CharField(
        max_length=100,
        help_text=_("optionally , add a brief note."),
        null=True,
        blank=True,
    )

    circle = models.ForeignKey(Circle,related_name="activities" ,on_delete=models.CASCADE ,null=True)
    participants = models.ManyToManyField(User, related_name="activities")

    done = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("activity")
        verbose_name_plural = _("activities")
        ordering = [
            "activity_date",
        ]

    def __str__(self):
        return self.get_activity_type_display()

    def get_absolute_url(self):
        return reverse("activity-detail", kwargs={"pk": self.pk})

    @property
    def icon(self):
        return self.ActivityTypeIcons[self.activity_type].value

    @property
    def remaining_eligible_ConfidentialRooms(self):
        """Return a QuerySet of the circle's companions who are not already activity participants."""  # noqa: E501
        # Only care group members are eligible to participate
        ConfidentialRooms = self.circle.ConfidentialRooms

        # Get current activity participants
        current_participants = self.participants.all()

        # Exclude existing companions from care group members
        remaining_eligible_ConfidentialRooms = ConfidentialRooms.difference(current_participants)

        return remaining_eligible_ConfidentialRooms




