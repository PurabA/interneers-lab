from abc import ABC, abstractmethod
from typing import List, Optional
from django_app.domain.product import Product
from datetime import datetime, timezone

# 1. The Rules
class ProductRepository(ABC):
    @abstractmethod
    def save(self, product:Product) -> Product:
        pass

    @abstractmethod
    def get_by_id(self,product_id:str)-> Optional[Product]:
        pass

    @abstractmethod
    # We add default pagination values here
    def get_all(self, limit: int = 10, offset: int = 0) -> List[Product]: 
        pass

    @abstractmethod
    def delete(self,product_id:str)->bool:
        pass


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

from mongoengine import Document, StringField, FloatField, IntField, DateTimeField

# --- THE TRANSLATOR (MongoEngine Schema) ---
class ProductDocument(Document):
    # This tells MongoDB to store these in a folder/collection called 'products'
    meta = {'collection': 'products'}
    
    # We define the exact columns our database will have
    product_id = StringField(required=True, unique=True) # Maps to our UUID
    name = StringField(required=True)
    description = StringField()
    category = StringField()
    price = FloatField()
    brand = StringField()
    quantity = IntField()

    # Sets the current UTC time automatically when a new product is saved
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    # We will update this one manually whenever changes are made
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

# --- THE NEW ADAPTER (MongoDB Implementation) ---
class MongoProductRepository(ProductRepository):
    
    def save(self, product: Product) -> Product:
        # 1. Translate Pure Python Product -> Mongo Document
        doc = ProductDocument(
            product_id=product.id,
            name=product.name,
            description=product.description,
            category=product.category,
            price=product.price,
            brand=product.brand,
            quantity=product.quantity
        )
        # 2. Save it to the real database! (MongoEngine handles the complex queries)
        doc.save() 
        return product

    def get_by_id(self, product_id: str) -> Optional[Product]:
        # Search the database for the matching ID
        doc = ProductDocument.objects(product_id=product_id).first()
        if not doc:
            return None
            
        # Translate the Mongo Document back into a Pure Python Product
        return Product(
            id=doc.product_id, name=doc.name, description=doc.description,
            category=doc.category, price=doc.price, brand=doc.brand, quantity=doc.quantity
        )

    def get_all(self, limit: int = 10, offset: int = 0) -> List[Product]:
        # Fetch a slice of documents from the database (Pagination!)
        docs = ProductDocument.objects.skip(offset).limit(limit)
        
        # Translate all of them back into Pure Python Products
        return [Product(
            id=d.product_id, name=d.name, description=d.description,
            category=d.category, price=d.price, brand=d.brand, quantity=d.quantity
        ) for d in docs]

    def delete(self, product_id: str) -> bool:
        # Find it and delete it from the database
        doc = ProductDocument.objects(product_id=product_id).first()
        if doc:
            doc.delete()
            return True
        return False