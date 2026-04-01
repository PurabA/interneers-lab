from typing import List, Optional
from django_app.domain.product import Product
from django_app.port.product_repository import ProductRepository
from django_app.entities.product import ProductDocument

class MongoProductRepository(ProductRepository):
    def save(self, product: Product) -> Product:
        doc = ProductDocument(
            product_id=product.id, name=product.name, description=product.description,
            category=product.category, price=product.price, brand=product.brand, quantity=product.quantity
        )
        doc.save() 
        return product

    def get_by_id(self, product_id: str) -> Optional[Product]:
        doc = ProductDocument.objects(product_id=product_id).first()
        if not doc: return None
        return Product(id=doc.product_id, name=doc.name, description=doc.description, category=doc.category, price=doc.price, brand=doc.brand, quantity=doc.quantity)

    def get_all(self, limit: int = 10, offset: int = 0) -> List[Product]:
        docs = ProductDocument.objects.skip(offset).limit(limit)
        return [Product(id=d.product_id, name=d.name, description=d.description, category=d.category, price=d.price, brand=d.brand, quantity=d.quantity) for d in docs]

    def delete(self, product_id: str) -> bool:
        doc = ProductDocument.objects(product_id=product_id).first()
        if doc:
            doc.delete()
            return True
        return False