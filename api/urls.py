
from django.urls import path

from . import views as v
from .views import SingleEventView


app_name = "api"

urlpatterns = [
    path('', v.home, name="home"),
    path('events', v.event, name="events"),
    path('participant/', v.paticipant_add, name='participant-add'),
    path('participant/login', v.participant_login, name="participant-login"),
    path('participant/logout', v.participant_logout, name="participant-logout"),
    path('events/<int:id>', SingleEventView.as_view(), name="event"),
]
