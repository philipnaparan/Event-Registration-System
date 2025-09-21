from django import forms

from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate

from .models import Event, EventType

class EventTypeForm(forms.ModelForm):
    class Meta:
        model = EventType
        fields = ['name']
        labels = {
            'name': 'Event Type Name',
        },
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        
        return cleaned_data
    


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'event_type', 'date_time', 'location', 'description', 'max_participants', 'event_photo']
        labels = {
            'name': 'Event Name',
            'event_type': 'Type of Event',
            'date_time': 'Date Time',
            'location': 'Location',
            'description': 'Description',
            'max_participants': 'Maximum No of Participants',
            'event_photo': 'Event Photo'
        },
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'event_type': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'date_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': 'required'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required'}),
        }

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['event_type'].queryset = self.fields['event_type'].queryset.order_by('name')
        self.fields['event_photo'].widget.attrs['class'] = 'imageinput form-control'


    def clean(self):
        cleaned_data = super().clean()

        max_participants = self.cleaned_data.get('max_participants', 0)
        if max_participants < 1 or max_participants > 100000:
            raise forms.ValidationError('Enter a valid max participants (ex. 100).')
        
        
        return cleaned_data
    

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}), max_length=50, required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}), max_length=30, required=True)