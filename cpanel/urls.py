
from django.urls import path

from . import views as v


app_name = "cpanel"

urlpatterns = [
    path('', v.home, name="home"),
    path('login/', v.login_user, name="login"),
    path('logout/', v.logout_user, name="logout"),

    # Event
    path('events/', v.EventListView.as_view(), name='events'),
    path('events/import/', v.EventImportView.as_view(), name='event_import'),
    path('events/add/', v.EventAddView.as_view(), name='event_add'),
    path('events/edit/<int:id>/', v.EventEditView.as_view(), name='event_edit'),
    path('events/delete/<int:id>/', v.EventDeleteView.as_view(), name='event_delete'),

    # Event Type
    path('event_types/', v.EventTypeListView.as_view(), name='event_types'),
    path('event_types/add/', v.EventTypeAddView.as_view(), name='event_type_add'),
    path('event_types/edit/<int:id>/', v.EventTypeEditView.as_view(), name='event_type_edit'),
    path('event_types/delete/<int:id>/', v.EventTypeDeleteView.as_view(), name='event_type_delete'),
]
