from django.apps import AppConfig
from mongoengine import connect

class DjangoAppConfig(AppConfig):
    # This tells Django this config belongs to our 'django_app' folder
    name = 'django_app' 

    # The ready() function automatically runs ONCE when the server starts!
    def ready(self):
        print("🚀 Starting up: Connecting to MongoDB...")
        connect(host="mongodb://root:example@127.0.0.1:27019/?authSource=admin")