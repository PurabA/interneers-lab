from typing import List, Optional
from django_app.domain.category import ProductCategory
from django_app.port.category_repository import CategoryRepository
from django_app.entities.category import CategoryDocument

class MongoCategoryRepository(CategoryRepository):
    def save(self, category: ProductCategory) -> ProductCategory:
        doc = CategoryDocument(
            category_id=category.id,
            title=category.title,
            description=category.description
        )
        doc.save()
        return category

    def get_by_id(self, category_id: str) -> Optional[ProductCategory]:
        doc = CategoryDocument.objects(category_id=category_id).first()
        if not doc: 
            return None
        return ProductCategory(id=doc.category_id, title=doc.title, description=doc.description)

    def get_all(self) -> List[ProductCategory]:
        docs = CategoryDocument.objects()
        return [ProductCategory(id=d.category_id, title=d.title, description=d.description) for d in docs]