from django.contrib import admin


from .models import Circle, ConfidentialRoom, JoinRequest

# Register your models here.


class ConfidentialRoomInline(admin.StackedInline):
    model = ConfidentialRoom
    extra = 0


@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    inlines = [
        ConfidentialRoomInline,
    ]


@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ("user","circle","status")
    
