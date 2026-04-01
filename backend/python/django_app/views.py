import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dataclasses import asdict

# Import our Port and Service
# from django_app.port.product_repository import InMemoryProductRepository
from django_app.port.product_repository import MongoProductRepository
from django_app.application_service.product_service import ProductService

# --- THE WIRING (Dependency Injection) ---
# We create ONE global instance of our dictionary database. 
# If we put this inside the view function, it would reset to empty on every single request!
# in_memory_db = InMemoryProductRepository()
real_mongo_db = MongoProductRepository()

# We hand the database to our service
product_service = ProductService(repository=real_mongo_db)


# --- THE WAITER (The View) ---
@csrf_exempt # This disables a security check just so we can test APIs easily locally
def product_list_create_view(request):
    
    # 1. HANDLE GET REQUESTS (Fetch all products with pagination)
    if request.method == 'GET':
        try:
            # Grab pagination rules from the URL (e.g., ?limit=5&offset=10)
            # We provide defaults (limit=10, offset=0) if the user doesn't provide them
            limit = int(request.GET.get('limit', 10))
            offset = int(request.GET.get('offset', 0))
            
            # Ask the Chef for the products
            products = product_service.get_all_products(limit=limit, offset=offset)
            
            # Translate Python dataclasses into standard dictionaries so Django can send them as JSON
            data = [asdict(p) for p in products]
            return JsonResponse({"data": data}, status=200)
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    # 2. HANDLE POST REQUESTS (Create a new product)
    elif request.method == 'POST':
        try:
            # Read the JSON data the user sent in the web request
            body = json.loads(request.body)
            
            # Hand the data to the Chef. If validation fails, the Chef raises a ValueError!
            new_product = product_service.create_product(
                name=body.get('name'),
                description=body.get('description'),
                category=body.get('category'),
                price=body.get('price'),
                brand=body.get('brand'),
                quantity=body.get('quantity')
            )
            
            # If successful, return the new product as JSON with a 201 (Created) status
            return JsonResponse(asdict(new_product), status=201)
            
        except ValueError as e:
            # Meaningful error messages! (Requirement from Week 2)
            return JsonResponse({"error": str(e)}, status=400) # 400 means "Bad Request"
        except Exception as e:
            return JsonResponse({"error": "Something went wrong processing your request."}, status=500)

@csrf_exempt
def product_detail_view(request, product_id):
    
    # HANDLE DELETE REQUESTS
    if request.method == 'DELETE':
        try:
            # Ask the Chef to delete the product
            result = product_service.delete_product(product_id)
            
            # 200 means "OK, request succeeded"
            return JsonResponse(result, status=200) 
            
        except ValueError as e:
            # If the ID is fake, the Service raises a ValueError. 
            # 404 means "Not Found"
            return JsonResponse({"error": str(e)}, status=404) 
        except Exception as e:
            return JsonResponse({"error": "Something went wrong."}, status=500)
            
    # If they try to GET or POST to this specific URL, we say "Method Not Allowed" (405)
    return JsonResponse({"error": "Method not allowed on this URL."}, status=405)