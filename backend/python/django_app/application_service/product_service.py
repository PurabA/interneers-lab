from typing import List, Dict, Any
import csv
import io
from django_app.domain.product import Product
from django_app.port.product_repository import ProductRepository
from django_app.port.category_repository import CategoryRepository

class ProductService:
    def __init__(self, product_repo: ProductRepository,category_repo: CategoryRepository):      
        self.product_repo = product_repo
        self.category_repo = category_repo

    def create_product(self, name: str, description: str, category_id: str, price: float, brand: str, quantity: int=0) -> Product:
        
        # Validation Checks
        if price <= 0:
            raise ValueError("Invalid Error: Price must be greater than zero.")
        if quantity < 0:
            raise ValueError("Invalid Error: Quantity cannot be negative.")
        if not name or not brand:
            raise ValueError("Invalid Error: Product name and brand are required.")

        category = self.category_repo.get_by_id(category_id)
        if not category:
            raise ValueError(f"Category with ID {category_id} does not exist. Cannot create product.")
        
        # DOMAIN Call
        new_product = Product.create_new(
            name=name, 
            description=description, 
            category_id=category_id, 
            price=price, 
            brand=brand, 
            quantity=quantity
        )
               
        return self.product_repo.save(new_product) #PORT Call

    # We tell the service to accept the pagination rules
    def get_all_products(self, limit: int = 10, offset: int = 0, filters: dict = None) -> List[Product]:
        
        return self.product_repo.get_all(limit=limit, offset=offset, filters=filters) #PORT Call


    def get_product(self, product_id: str) -> Product:
        product = self.product_repo.get_by_id(product_id) #PORT Call
        if not product:
            
            raise ValueError(f"Not Found: Product with ID {product_id} does not exist.")
        return product

    def bulk_upload_products(self, csv_file_bytes: bytes) -> dict:
        # 1. Decode the raw file from the internet into readable text
        decoded_file = csv_file_bytes.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded_file))
        
        products_to_save = []
        errors = []
        row_number = 1

        # 2. Read the spreadsheet row by row
        for row in csv_reader:
            row_number += 1
            try:
                # Extract data from the CSV columns
                name = row.get('name')
                price = float(row.get('price', 0))
                brand = row.get('brand')
                category_id = row.get('category_id')
                description = row.get('description', '')
                quantity = int(row.get('quantity', 0))

                # Validate data (just like we do for a single product)
                if not name or not name.strip():
                    raise ValueError("Product name is required.")
                if price <= 0:
                    raise ValueError("Price must be greater than zero.")
                if quantity < 0:
                    raise ValueError("Quantity cannot be negative.")
                if not brand or not brand.strip():
                    raise ValueError("Brand is required.")
                if not self.category_repo.get_by_id(category_id):
                    raise ValueError(f"Category ID {category_id} not found.")

                # Create the Pure Python product
                product = Product.create_new(
                    name=name, description=description, category_id=category_id,
                    price=price, brand=brand, quantity=quantity
                )
                products_to_save.append(product)

            except Exception as e:
                # If one row fails, we don't crash the whole app. We just log the error!
                errors.append(f"Row {row_number} failed: {str(e)}")

        # 3. Hand the massive list to the Repository for a bulk insert
        inserted_count = 0
        if products_to_save:
            inserted_count = self.product_repo.save_many(products_to_save)

        # 4. Return a summary to the user
        return {
            "success_count": inserted_count,
            "error_count": len(errors),
            "errors": errors
        }

    def delete_product(self, product_id: str) -> dict:
        success = self.product_repo.delete(product_id) #PORT Call
        if not success:
            raise ValueError(f"Not Found: Cannot delete. Product with ID {product_id} does not exist.")
        return {"message": "Product successfully deleted."}