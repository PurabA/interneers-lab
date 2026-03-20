from django.contrib import admin
from django.urls import path
from django.http import HttpResponse, JsonResponse
from django_app.port.greeting_view import greeting_view
from django_app import views

def hello_world(request):
    # return HttpResponse("Hello, world! This is Rippling's interneers-lab Django server.")
    name = request.GET.get('name', 'world')
    return JsonResponse({"message": f"Hello, {name}! This is Rippling's interneers-lab Django server!"})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', hello_world),
    path('greeting/', greeting_view),
    path('products/', views.product_list_create_view, name='product-list-create'),
]
