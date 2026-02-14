Greeting Service: Hexagonal Architecture
-----------------------------------------
This is a simple Django-based server demonstrating Hexagonal Architecture (Ports and Adapters). The goal is to keep the business logic (the "Domain") completely separated from the web framework (Django).

The Hexagonal Structure
------------------------
The project is organized into layers to ensure the core logic is independent of the delivery mechanism:

- Domain (domain/greeting.py): Contains the Greeting class. This is where the actual "logic of greeting" lives. It doesn't know Django exists.

- Application Service (application_service/greeting_service.py): Acts as a bridge. The GreetingService orchestrates the domain logic for the outside world.

- Ports/Adapters (port/greeting_view.py): The web layer. This handles the HTTP request, extracts the name parameter, and returns a JSON response.


How it Works
-------------
- When a request hits the /greeting/ endpoint:

- The View receives the request.

- The Service is called to handle the business flow.

- The Domain generates the specific greeting string.

API Endpoints
GET /hello/?name=<your_name>: A simple direct greeting.

GET /greeting/?name=<your_name>: A greeting processed through the Hexagonal layers.

Quick Start
------------
Ensure Django is installed.

Run the server: python manage.py runserver.

Test the logic:

Bash
curl "http://localhost:8000/greeting/?name=Engineer"
Response:
{"message": "Hello Engineer, this is our logic of greeting!"}



Project Structure
-----------------
django_app/
├── domain/              # Pure business logic (Greeting)
├── application_service/ # Orchestration (GreetingService)
├── port/                # Entry points/Views (greeting_view)
└── urls.py              # URL Routing
