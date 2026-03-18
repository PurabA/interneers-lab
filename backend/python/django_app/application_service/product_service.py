from typing import List, Dict, Any
from django_app.domain.product import Product
from django_app.port.product_repository import ProductRepository

class ProductService:
    def __init__(self, repository: ProductRepository):      
        self.repository = repository

    def create_product(self, name: str, description: str, category: str, price: float, brand: str, quantity: int) -> Product:
        
        # Validation Checks
        if price <= 0:
            raise ValueError("Invalid Error: Price must be greater than zero.")
        if quantity < 0:
            raise ValueError("Invalid Error: Quantity cannot be negative.")
        if not name or not brand:
            raise ValueError("Invalid Error: Product name and brand are required.")

        # DOMAIN Call
        new_product = Product.create_new(
            name=name, 
            description=description, 
            category=category, 
            price=price, 
            brand=brand, 
            quantity=quantity
        )
               
        return self.repository.save(new_product) #PORT Call

    # We tell the service to accept the pagination rules
    def get_all_products(self, limit: int = 10, offset: int = 0) -> List[Product]:
        
        return self.repository.get_all(limit=limit, offset=offset) #PORT Call


    def get_product(self, product_id: str) -> Product:
        product = self.repository.get_by_id(product_id) #PORT Call
        if not product:
            
            raise ValueError(f"Not Found: Product with ID {product_id} does not exist.")
        return product

    def delete_product(self, product_id: str) -> dict:
        success = self.repository.delete(product_id) #PORT Call
        if not success:
            raise ValueError(f"Not Found: Cannot delete. Product with ID {product_id} does not exist.")
        return {"message": "Product successfully deleted."}