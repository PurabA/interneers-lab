import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dataclasses import asdict
from django_app.adapters.mongo_category import MongoCategoryRepository
from django_app.application_service.category_service import CategoryService
# from django_app.port.product_repository import InMemoryProductRepository
from django_app.adapters.mongo import MongoProductRepository
from django_app.application_service.product_service import ProductService

# in_memory_db = InMemoryProductRepository()
real_mongo_db = MongoProductRepository()
category_db = MongoCategoryRepository()
category_service = CategoryService(repository=category_db)

product_service = ProductService(product_repo=real_mongo_db, category_repo=category_db)


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
            
            # Extract filters from the URL!
            filters = {}
            if 'category' in request.GET: filters['category'] = request.GET['category']
            if 'min_price' in request.GET: filters['min_price'] = request.GET['min_price']
            if 'max_price' in request.GET: filters['max_price'] = request.GET['max_price']
            if 'brand' in request.GET: filters['brand'] = request.GET['brand']
            
            # Ask the Chef for the products
            products = product_service.get_all_products(limit=limit, offset=offset, filters=filters if filters else None)
            
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
                category_id=body.get('category_id'),
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

@csrf_exempt
def category_list_create_view(request):
    if request.method == 'GET':
        categories = category_service.get_all_categories()
        data = [{"id": c.id, "title": c.title, "description": c.description} for c in categories]
        return JsonResponse({"categories": data}, status=200)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            category = category_service.create_category(
                title=data['title'],
                description=data.get('description', '')
            )
            return JsonResponse({
                "message": "Category created!", 
                "category": {"id": category.id, "title": category.title}
            }, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
def product_bulk_upload_view(request):
    if request.method == 'POST':
        # Check if the user actually attached a file called 'file'
        if 'file' not in request.FILES:
            return JsonResponse({"error": "No file uploaded. Please attach a CSV file under the key 'file'."}, status=400)
            
        csv_file = request.FILES['file']
        
        # Check if it's a CSV
        if not csv_file.name.endswith('.csv'):
            return JsonResponse({"error": "Invalid file type. Only .csv is allowed."}, status=400)

        try:
            # Pass the raw file data to the Chef!
            result = product_service.bulk_upload_products(csv_file.read())
            return JsonResponse(result, status=200 if result['error_count'] == 0 else 207)  # 207 means "Multi-Status"
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed. Use POST."}, status=405)