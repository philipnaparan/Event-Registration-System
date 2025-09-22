from django.http import HttpResponse, HttpResponseNotFound
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.conf import settings
from django.db import IntegrityError
from django.core.files.storage import FileSystemStorage

from datetime import datetime


from .models import Event, EventType
from .forms import LoginForm, EventForm, EventTypeForm

import csv
import os
import random
import string
import zipfile
import shutil

@login_required(login_url='cpanel:login')
def home(request):
    context = dict()
    context['page_title'] = "Home"
    context['data'] = "Halo halo " + datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    return render(request, 'cp_home.html', context)


def login_user(request):
    
    form = None
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():

            user =  form.get_user()

            if user:
                login(request, user)

                request.session.set_expiry(900) #15 min.
                return redirect('cpanel:home')
            else:
                messages.warning(request, "Login failed. Account not found.")

        else:
            messages.warning(request, "Login failed. Wrong email or password..")

    else:
        if request.user.is_authenticated:
            return redirect('cpanel:home')
        else:
            form = LoginForm()
    
    return render(request, 'cp_login.html', context={'form': form})


def logout_user(request):
    if request.session:
        request.session.flush()
    
    logout(request)
    messages.success(request, "Logout successfullly.")
    return redirect("cpanel:login")





class EventListView(LoginRequiredMixin, View):
    login_url = 'cpanel:login'

    def get(self, request):
        events = Event.objects.all().order_by('-date_time')
        return render(request, 'cp_event_list.html', {'events': events})
    

class EventImportView(LoginRequiredMixin, View):
    login_url = 'cpanel:login'

    context = dict()
    context['success'] = 0
    context['msg'] = ""
    context['ts'] = datetime.now()

    def get(self, request):
        return render(request, 'cp_event_import.html', self.context)

    def post(self, request):

        if 'event-files' not in request.FILES:
            self.context['msg'] = 'Error: No file attachment found.'
            return render(request, 'cp_event_import.html', self.context)

        
        uploaded_file = request.FILES['event-files']

        if not uploaded_file.name.endswith('.zip') or uploaded_file.size > 4 * 1024 * 1024: # limit to 4MB
            self.context['msg'] = 'Error: Zip file is required or file exceed 4MB.'
            return render(request, 'cp_event_import.html', self.context)
        
        # create temporary working directory
        working_folder = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        working_path = os.path.join(settings.MEDIA_ROOT, 'temp', working_folder)
        os.makedirs(working_path)


        try:
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                zip_ref.extractall(working_path)
                

            event_data_csv = os.path.join(working_path, 'event_data.csv')

            if not os.path.isfile(event_data_csv):
                self.context['msg'] = 'Error: The required event_data.csv is missing in the uploaded zip file.'
                return render(request, 'cp_event_import.html', self.context)
            


            with open(event_data_csv) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')

                cols = dict()
                num_row = 0
                num_col = 0
                imported = 0
                for row in csv_reader:
                    # header part
                    if num_row == 0:
                        for col in row:
                            cols[col] = num_col
                            num_col += 1

                        num_row += 1
                        continue

                    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'events'))
                    src_event_photo = None
                    print("NAME:", row[cols['name']] , "EVENT PHOTO: ", row[cols['event_photo']] ,sep="   ")
                    if row[cols['event_photo']]:
                        src_event_photo = os.path.join(working_path, 'event_photo', row[cols['event_photo']])

                    try:
                        event_type, _ = EventType.objects.get_or_create(name=row[cols['event_type']])
                        
                        new_event = Event()
                        new_event.name = row[cols['name']]
                        new_event.date_time = datetime.strptime(row[cols['date_time']], '%d/%m/%Y')
                        new_event.location = row[cols['location']]
                        new_event.description = row[cols['description']]
                        new_event.max_participants = row[cols['max_participants']]
                        new_event.event_type = event_type
                        if src_event_photo and os.path.exists(src_event_photo):
                            #get back the saved file from fs
                            src_event_photo = fs.save( row[cols['event_photo']], open(src_event_photo, 'rb'))
                            new_event.event_photo = os.path.join('events', src_event_photo)

                        
                        new_event.save()
                        imported += 1
                    except IntegrityError  as e:
                        print("INTEGRETIY ERROR WHILE SAVING!")

                    #print(  src_event_photo, sep="    "  )

                if imported > 0 :
                    self.context['success'] = 1
                    self.context['msg'] = f'Success! A total of {str(imported)} new Events has been imported.'
                    return render(request, 'cp_event_import_success.html', self.context)
                else:
                    self.context['msg'] = 'File is fine but no record has been added.'
                    return render(request, 'cp_event_import.html', self.context)

        except Exception as e:
            self.context['msg'] = f'Error while extracting uploaded file. Ref: {str(e)}'
            return render(request, 'cp_event_import.html', self.context)
        finally:
            shutil.rmtree(working_path)

        return render(request, 'cp_event_import.html', self.context)

class EventAddView(LoginRequiredMixin, View):
    login_url = 'cpanel:login'

    def get(self, request):
        form = EventForm()
        return render(request, 'cp_event_add.html', {'form': form})

    def post(self, request):
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('cpanel:events')
        return render(request, 'cp_event_add.html', {'form': form})

class EventEditView(LoginRequiredMixin, View):
    login_url = 'cpanel:login'

    def get(self, request, id):
        event = get_object_or_404(Event, id=id)
        form = EventForm(instance=event)
        return render(request, 'cp_event_edit.html', {'form': form, 'event': event})

    def post(self, request, id):
        event = get_object_or_404(Event, id=id)
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect('cpanel:events')
        return render(request, 'cp_event_edit.html', {'form': form, 'event': event})

class EventDeleteView(LoginRequiredMixin, View):
    login_url = 'cpanel:login'

    def get(self, request, id):
        event = get_object_or_404(Event, id=id)
        return render(request, 'cp_event_delete.html', {'event': event})

    def post(self, request, id):
        event = get_object_or_404(Event, id=id)
        event.delete()
        return redirect('cpanel:events')
    


class EventParticipantsView(LoginRequiredMixin, View):
    login_url = 'cpanel:login'

    def get(self, request, id):
        event = get_object_or_404(Event, id=id)
        participants = event.participant_set.all()
        print(participants)
        return render(request, 'cp_event_participants.html', {'event': event, 'participants' : participants})
    



class EventTypeListView(LoginRequiredMixin, View):
    login_url = 'cpanel:login'

    def get(self, request):
        types = EventType.objects.all().order_by('name')
        return render(request, 'cp_event_type_list.html', {'types': types})

class EventTypeAddView(LoginRequiredMixin, View):
    login_url = 'cpanel:login'

    def get(self, request):
        form = EventTypeForm()
        return render(request, 'cp_event_type_add.html', {'form': form})

    def post(self, request):
        form = EventTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cpanel:event_types')
        return render(request, 'cp_event_type_add.html', {'form': form})

class EventTypeEditView(LoginRequiredMixin, View):
    login_url = 'cpanel:login'

    def get(self, request, id):
        type = get_object_or_404(EventType, id=id)
        form = EventTypeForm(instance=type)
        return render(request, 'cp_event_type_edit.html', {'form': form, 'type': type})

    def post(self, request, id):
        type = get_object_or_404(EventType, id=id)
        form = EventTypeForm(request.POST, instance=type)
        if form.is_valid():
            form.save()
            return redirect('cpanel:event_types')
        return render(request, 'cp_event_type_edit.html', {'form': form, 'type': type})

class EventTypeDeleteView(LoginRequiredMixin, View):
    login_url = 'cpanel:login'

    def get(self, request, id):
        type = get_object_or_404(EventType, id=id)
        return render(request, 'cp_event_type_delete.html', {'type': type})

    def post(self, request, id):
        type = get_object_or_404(EventType, id=id)
        type.delete()
        return redirect('cpanel:event_types')
    


