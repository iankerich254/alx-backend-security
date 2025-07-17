from django.shortcuts import render
from django.http import JsonResponse
from ratelimit.decorators import ratelimit

# Anonymous: 5 req/min, Authenticated: 10 req/min
@ratelimit(key='ip', rate='10/m', method='GET', block=True)
@ratelimit(key='ip', rate='5/m', method='GET', block=True)
def login_view(request):
    if request.user.is_authenticated:
        return JsonResponse({"message": "Welcome back!"})
    else:
        return JsonResponse({"message": "Please log in."})
