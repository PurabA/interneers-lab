from typing import List, Optional
from django_app.domain.product import Product
from django_app.port.product_repository import ProductRepository

class InMemoryProductRepository(ProductRepository):

    def __init__(self):
        # This dictionary is our "database". 
        # The key will be the Product ID, and the value will be the Product object.
        self._storage = {} 

    def save(self, product: Product) -> Product:
        self._storage[product.id] = product
        return product

    def get_by_id(self, product_id: str) -> Optional[Product]:
        # Returns the product if found, otherwise returns None
        return self._storage.get(product_id)
    
    def get_all(self, limit: int = 10, offset: int = 0) -> List[Product]:
        
        all_products = list(self._storage.values())
        return all_products[offset : offset + limit]

    def delete(self, product_id: str) -> bool:
        if product_id in self._storage:
            del self._storage[product_id]
            return True
        return False