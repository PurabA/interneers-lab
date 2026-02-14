from django_app.domain.greeting import Greeting

class GreetingService:
    def greet(self, name:str):
        greeting = Greeting(name)
        return greeting.greeting_logic()
