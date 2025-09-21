
from django.http import response, JsonResponse
from django.shortcuts import redirect
from django.urls import resolve, reverse



class UserSessionCheckMiddleware():

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        response = self.get_response(request)
        current_url = resolve(request.path_info).url_name

        print("CURRENT URL: ", current_url)

        exempt = ['home', 'login', 'logout', 'event', 'events', 'participant-add', 'participant-login', 'participant-logout']

        if not request.user.is_authenticated and (current_url and current_url not in exempt):
            return redirect( reverse('cpanel:login') )
        elif request.user.is_authenticated:
            request.session.set_expiry(900)
            return response
        else:
            return response