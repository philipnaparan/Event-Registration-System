from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q, Count
from django.forms.models import model_to_dict
from django.core.exceptions import FieldError

from datetime import datetime, timedelta
import random
import hashlib
import base64


from cpanel.models import Event, Participant

def home(request):
    return HttpResponseNotFound()


def event(request):
    get = request.GET

    filter_data_from = get.get('event_from', default=None)
    filter_data_to = get.get('event_to', default=None)
    filter_text = get.get('q', default=None)
    sort_by = get.get('sort', default='-date_time')

    #token = get.get('token', default='')

    perpage = safe_int(get.get('perpage'), 10)
    page = safe_int(get.get('page'), 1)

    if page <= 0 : page =1

    events_data = []
    #participant_events = None

    try:
        if (filter_data_from and filter_data_to) or filter_text:
            filters = None
            if filter_text:
                filters =  Q(event_type__name__icontains = filter_text)
                filters.add(Q(name__icontains = filter_text), Q.OR)
                filters.add(Q(location__icontains = filter_text), Q.OR)

            if (filter_data_from and filter_data_to):
                print("FROM ", filter_data_from, " TO ", filter_data_to)
                filter_data_from = datetime.strptime( filter_data_from + ' 00:00:00', '%d-%m-%Y %H:%M:%S')
                filter_data_to = datetime.strptime( filter_data_to + ' 23:59:59', '%d-%m-%Y %H:%M:%S')
                print("FROM ", filter_data_from, " TO ", filter_data_to)

                if not filters:
                    filters = Q(date_time__range=[filter_data_from, filter_data_to])
                else:
                    filters.add(Q(date_time__range=[filter_data_from,filter_data_to]), Q.AND)

            if sort_by == 'relevant':
                events_data = Event.objects.filter(filters)
            else:
                events_data = Event.objects.filter(filters).order_by(sort_by)

            print("SQL: ", events_data.query)
        else:
            #events_data = Event.objects.all().order_by(sort_by) #.values('id', 'name', 'date_time', 'location', 'event_type__name')
            if sort_by == 'relevant':
                events_data =  Event.objects.all()
            else:
                events_data = Event.objects.all().order_by(sort_by)

            print("SQL: ", events_data.query, events_data)


        """ print("####### TOKEN: ", token)
        if token:
            valid, _ = validate_token(token)

            if valid:
                participant = Participant.objects.get(session_token = token)

                if participant:
                    participant_events = participant.event.all() """



    except FieldError as e:
        print("ERROR: ", e)
    except:
        pass


    record_info = {'max_page':1, 'total_records':0, 'page':1, 'per_page': perpage}
    data = []

    if events_data:

        record_info['total_records'] = events_data.count()
        record_info['max_page'] = record_info['total_records'] / perpage 
        if record_info['max_page'] % 1 > 0: 
            record_info['max_page'] = int(record_info['max_page']) + 1

        
        if page > record_info['max_page']:
            page = record_info['max_page']
            
        record_info['page'] = page
        record_info['per_page'] = perpage
        

        paginator = Paginator(events_data, per_page=perpage)
        try:
            events_data = paginator.page(number=page)
        except EmptyPage:
            events_data = []
        
        #data = [row for row in events_data]
        def get_available_participants(event):
            event_dict = model_to_dict(event)
            event_dict['date_time'] = event.date_time.strftime("%d/%m/%Y %I:%M %p")
            event_dict['type'] = event.event_type.name
            event_dict['available'] = event.max_participants - event.participant_set.count()
            event_dict['event_photo'] = event.event_photo.url if event.event_photo else 'events/default-photo.jpg'
            
            del event_dict['description'] 
            
            """ event_dict['is_registered'] = 0
            if participant_events:
                print("#################### ", participant_events)
                if event in participant_events:
                    event_dict['is_registered'] = 1 """

            return event_dict
        
        data = map(get_available_participants, events_data)
    
    return JsonResponse({'records': list(data), 'record_info': record_info})


@method_decorator(csrf_exempt, name='dispatch')
class SingleEventView(View):

    def get(self, request, id):

        token = request.GET.get('token', None)

        event = None
        participant_events = None
        result_status_code = 200

        try:

            event = Event.objects.get(id=id)
            
            if token and event:
                valid, _ = validate_token(token)

                if valid:
                    participant = Participant.objects.get(session_token = token)

                    if participant:
                        participant_events = participant.event.filter(id = event.id)
                else:
                    return JsonResponse({'records': {'msg': 'Invalid token.'}}, status=404)

        except FieldError as e:
            print("ERROR: ", e)
        except:
            pass
        

        data = dict()

        if event:
            data = model_to_dict(event)
            data['date_time'] = event.date_time.strftime("%d/%m/%Y %I:%M %p")
            data['type'] = event.event_type.name
            data['available'] = event.max_participants - event.participant_set.count()
            data['event_photo'] = event.event_photo.url if event.event_photo else 'events/default-photo.jpg'

            data['is_registered'] = 0
            if participant_events:
                if event in participant_events:
                    data['is_registered'] = 1

        else:
            return JsonResponse({'records': {'msg': 'Event not found.'}}, status=404)
        
        return JsonResponse({'records': data}, status=result_status_code)
    
    def post(self, request, id):
        
        token = request.POST.get('token', None)

        event = None
        participant = None
        result_status_code = 200

        try:

            event = Event.objects.get(id=id)
            
            if token and event:
                valid, _ = validate_token(token)

                if valid:
                    participant = Participant.objects.get(session_token = token)

                    if participant is None:
                        return JsonResponse({'records': {'msg': 'No participant.'}}, status=404)
                else:
                    return JsonResponse({'records': {'msg': 'Invalid token.'}}, status=404)

        except FieldError as e:
            print("ERROR: ", e)
        except e:
            pass
        

        dict()

        print(event, participant, sep=" ??? ")

        if event and participant:
            participant.event.add(event)

        else:
            return JsonResponse({'records': {'msg': 'Event not found.' }}, status=404)
        
        return JsonResponse({'records': {'msg': 'Success.'}}, status=result_status_code)



def safe_int(value, default = 0):
    try:
        return int(value)
    except:
        return default    
           

@csrf_exempt
def participant_login(request):
    get = request.POST

    fld_email = get.get('email', default=None)
    fld_password = get.get('password', default=None)
    token = get.get('token', default=None)

    result = dict()
    result_status_code = 200

    if not token and (not fld_email or not fld_password):
        result['msg'] = 'Missing required information.'
        result_status_code = 401  

        return JsonResponse({'result': result}, status=result_status_code)

    participant =  None
    session_valid = False

    try:
        if token:
            session_valid, _ = validate_token(token)

            if session_valid:
                participant = Participant.objects.get(session_token = token)

        else:
            participant = Participant.objects.get(email=fld_email)
    except Participant.DoesNotExist:
        pass

    if participant:

        #stored_password = hashlib.sha1(participant.password.encode('utf-8')).hexdigest()
        stored_password = participant.password

        if  fld_password == stored_password or session_valid:

            if not token:

                token = generate_session_token()
                participant.session_token = token
                participant.save(update_fields=['session_token',])

            result['msg'] = 'Success!'
            result['record'] = {'first_name': participant.first_name,'last_name': participant.last_name,'profile_picture': participant.profile_picture.url if participant.profile_picture else '', 'phone_no':participant.phone_no, 'email':participant.email}
            result['token'] = token
        else:
            result['msg'] = 'Wrong password.'
            result_status_code = 401  
    else:
        result['msg'] = 'Account not found.' 
        result_status_code = 401   


        
    return JsonResponse({'result': result}, status=result_status_code)


def generate_session_token():

    session_no = str(random.randrange(1000000, 9999999)) + '@' + str(random.randrange(1000000, 9999999))
    session_no = base64.b64encode(session_no.encode('utf-8')).decode('utf-8')

    expiry = datetime.now() + timedelta(hours=3) #valid for 3hrs
    expiry = expiry.strftime("%d-%m-%Y %H:%M:%S")
    expiry = base64.b64encode(expiry.encode('utf-8')).decode('utf-8')

    token = f'{session_no},{expiry}'
    token = base64.b64encode(token.encode('utf-8')).decode('utf-8')
    
    return token

@csrf_exempt
def participant_logout(request):
    get = request.POST

    session_token = get.get('token', default=None)

    result = dict()
    result_status_code = 200

    if not session_token:
        result['msg'] = 'Missing required information.'
        result_status_code = 401

        return JsonResponse({'result': result})

    participant = None
    
    try:
        participant = Participant.objects.get(session_token=session_token)
    except Participant.DoesNotExist:
        pass

    if participant:
        participant.session_token = ''
        participant.save(update_fields=['session_token',])

        result['msg'] = 'Success!'
    else:
        result['msg'] = 'Invalid session token.' 
        result_status_code = 401


    return JsonResponse({'result': result}, status=result_status_code)

@csrf_exempt
def paticipant_add(request):
    
    if request.method == 'POST':

        result = dict()
        result_status_code = 200

        get = request.POST
        files = request.FILES

        fld_mode = get.get('mode', 'add')
        fld_token = get.get('token', None)

        fld_fname = get.get('fname', None)
        fld_lname = get.get('lname', None)
        fld_phone = get.get('phone', None)
        fld_email = get.get('email', None)
        fld_password = get.get('password', None)
        fld_new_password = get.get('new_password', None)

        if fld_mode == 'add':
            # req for add mode
            if not fld_fname or not fld_lname or not fld_phone or not fld_email or not fld_password:
                result['msg'] = 'Missing required information.' 
                return JsonResponse({'result': result}, status=401)
        
            
            participant = Participant.objects.get(email=fld_email)
            if participant:
                result['msg'] = 'E-mail already exist.' 
                return JsonResponse({'result': result}, status=409)
        else: 
            # req for edit mode
            if not fld_fname or not fld_lname or not fld_phone or not fld_email or not fld_token:
                result['msg'] = 'Missing required information.' 
                return JsonResponse({'result': result}, status=401)


        uploaded_file = None

        try:
            uploaded_file = files.get('photo')
            if uploaded_file:
                max_size = 2 * 1024 * 1024  # 2MB

                if uploaded_file.size > max_size:
                    result['msg'] = 'File should not exceed 2MB.' 
                    return JsonResponse({'result': result}, status=401)

        except Exception as e:
            result['msg'] = str(e) 
            return JsonResponse({'result': result}, status=401)
        
        
        participant = None
        
        
        try:

            hashed_password = None
            
            if fld_password:
                hashed_password = hashlib.sha1(fld_password.encode('utf-8')).hexdigest()

            if(fld_mode == 'add'):
                #for add mode
                participant = Participant(
                    first_name = fld_fname,
                    last_name = fld_lname,
                    email = fld_email,
                    phone_no = fld_phone,
                    password = hashed_password,
                    profile_picture = uploaded_file,
                    session_token = generate_session_token()
                )

                participant.save()

                if participant:
                    result['token'] = participant.session_token
            else:
                # for edit mode

                session_valid = False

                try:
                    if fld_token:
                        session_valid, _ = validate_token(fld_token)

                        if session_valid:
                            participant = Participant.objects.get(session_token = fld_token)
                        else:
                            result['msg'] = 'Session expired.' 
                            return JsonResponse({'result': result}, status=401)
                            
                except Participant.DoesNotExist:
                    result['msg'] = 'Participant account not found.' 
                    return JsonResponse({'result': result}, status=401)

                participant = Participant.objects.get(session_token = fld_token)

                if participant:

                    participant.first_name = fld_fname
                    participant.last_name = fld_lname
                    participant.phone_no = fld_phone
                    participant.email = fld_email

                    xparticipant = Participant.objects.get(email=fld_email)
                    if xparticipant and xparticipant.id != participant.id:
                        result['msg'] = 'E-mail already exist.' 
                        return JsonResponse({'result': result}, status=409)

                    updated_fields = ['first_name','last_name','phone_no','email']

                    # compare stored password to the old password given
                    if hashed_password:
                        if hashed_password == participant.password:
                            
                            if fld_new_password:
                                fld_new_password = hashlib.sha1(fld_new_password.encode('utf-8')).hexdigest()

                                participant.password = fld_new_password
                                updated_fields.append('password')
                            
                        else:
                            result['msg'] = 'Wrong old password.' 
                            return JsonResponse({'result': result}, status=401)

                    # there is an update to profile photo
                    if uploaded_file:
                        participant.profile_picture = uploaded_file
                        updated_fields.append('profile_picture')

                    participant.save(update_fields=updated_fields)

                    result['msg'] = 'Success! Profile has been updated.' 
                    result['record'] = {'first_name': participant.first_name,'last_name': participant.last_name,'profile_picture': participant.profile_picture.url if participant.profile_picture else '', 'phone_no':participant.phone_no, 'email':participant.email}


        except Exception as e:
            result['msg'] = str(e) 
            return JsonResponse({'result': result}, status=401)
        


        return JsonResponse({'result': result}, status=result_status_code)
        


def validate_token(token):
    
    valid = False
    token_data = []

    try:
        token_data = base64.b64decode(token.encode('utf-8')).decode('utf-8')
        token_data = token_data.split(',')

        expiry = base64.b64decode(token_data[1].encode('utf-8')).decode('utf-8')

        sec_diff = ( datetime.strptime(expiry, '%d-%m-%Y %H:%M:%S') - datetime.now() ).total_seconds()

        if sec_diff > 0:
            valid = True
    except Exception as e:
        print("ERROR: ", e)

    return valid, token_data