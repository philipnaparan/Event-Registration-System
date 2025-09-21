from django.db import models

class EventType(models.Model):
    name = models.CharField('Type Name', max_length=100, null=False)

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField('Name', max_length=250, null=False)
    date_time = models.DateTimeField('Date Time', null=False)
    location = models.CharField(max_length=250)
    description = models.CharField(max_length=1000)
    max_participants = models.IntegerField()
    event_type = models.ForeignKey(EventType, on_delete=models.RESTRICT, blank=True, null=True)
    event_photo = models.ImageField(upload_to="events", default='events/no-photo.jpg', null=True, blank=True)

    def __str__(self):
        return self.name


class Participant(models.Model):
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=False)
    profile_picture = models.ImageField(upload_to="participants", default='participants/no-photo.jpg', null=True, blank=True)
    email = models.EmailField('Email Address', max_length=50, unique=True, null=False)
    phone_no = models.CharField('Phone Number', max_length=20, null=False)
    event = models.ManyToManyField(Event)
    password = models.CharField(max_length=250, null=False, default='')
    session_token = models.CharField(max_length=1000, default='', null=True, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
