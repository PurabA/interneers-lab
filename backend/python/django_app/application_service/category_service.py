from typing import List
from django_app.domain.category import ProductCategory
from django_app.port.category_repository import CategoryRepository

class CategoryService:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def create_category(self, title: str, description: str = "") -> ProductCategory:
        # Create the pure python object
        category = ProductCategory.create_new(title=title, description=description)
        # Save it to the database
        return self.repository.save(category)

    def get_all_categories(self) -> List[ProductCategory]:
        return self.repository.get_all()