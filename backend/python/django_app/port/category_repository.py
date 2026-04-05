from abc import ABC, abstractmethod
from typing import List, Optional
from django_app.domain.category import ProductCategory

class CategoryRepository(ABC):
    @abstractmethod
    def save(self, category: ProductCategory) -> ProductCategory: 
        pass

    @abstractmethod
    def get_by_id(self, category_id: str) -> Optional[ProductCategory]: 
        pass

    @abstractmethod
    def get_all(self) -> List[ProductCategory]: 
        pass