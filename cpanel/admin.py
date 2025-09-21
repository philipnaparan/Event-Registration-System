from django.contrib import admin

from .models import Event, Participant,  EventType

admin.site.register(EventType)




@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'event_type')
    search_fields = ('name', 'location')
    list_filter = ('date_time', 'event_type')
    fieldsets = (
        ('Event Information', {
            'fields': (
                'name', 'event_type', 'date_time', 'location', 'description', 'max_participants', 'event_photo'
            ),
        }),
    )


class ParticipantEventInline(admin.StackedInline):
    model = Participant.event.through
    extra = 0


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_no', 'email')
    search_fields = ('first_name', 'last_name', 'phone_no', 'email')
    list_filter = ('event',)
    fieldsets = (
        ('Participant Information', {
            'fields': (
                'first_name', 'last_name', 'email', 'phone_no'
            ),
        }),
        ('Photo', {
            'fields': (
                'profile_picture',
            ),
        }),
        ('Login Details', {
            'fields': (
                'password', 'session_token'
            ),
        }),
    )
    inlines = [ParticipantEventInline]
    raw_id_fields = ('event',)