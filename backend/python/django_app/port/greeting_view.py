from django.http import HttpResponse, JsonResponse
from django_app.application_service.greeting_service import GreetingService 

def greeting_view(request):
    name = request.GET.get('name', 'world')
    greeting_service = GreetingService()
    message = greeting_service.greet(name)
    return JsonResponse({"message": message})

