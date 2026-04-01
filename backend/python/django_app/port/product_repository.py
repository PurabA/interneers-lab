from abc import ABC, abstractmethod
from typing import List, Optional
from django_app.domain.product import Product

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
