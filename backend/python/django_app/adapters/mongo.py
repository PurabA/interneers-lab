from typing import List, Optional
from django_app.domain.product import Product
from django_app.port.product_repository import ProductRepository
from django_app.entities.product import ProductDocument
from django_app.entities.category import CategoryDocument

class MongoProductRepository(ProductRepository):
    def save(self, product: Product) -> Product:
        # Fetch the CategoryDocument reference by ID
        category_doc = CategoryDocument.objects(category_id=product.category_id).first() if product.category_id else None
        
        doc = ProductDocument(
            product_id=product.id, name=product.name, description=product.description,
            category=category_doc, price=product.price, brand=product.brand, quantity=product.quantity
        )
        doc.save() 
        return product

    def get_by_id(self, product_id: str) -> Optional[Product]:
        doc = ProductDocument.objects(product_id=product_id).first()
        if not doc: return None
        return Product(id=doc.product_id, name=doc.name, description=doc.description, category_id=doc.category.category_id if doc.category else None, price=doc.price, brand=doc.brand, quantity=doc.quantity)

    def get_all(self, limit: int = 10, offset: int = 0, filters: dict = None) -> List[Product]:
        # Start with all objects
        query = ProductDocument.objects
        
        # Apply filters if they exist!
        if filters:
            if 'category' in filters:
                # Filter by category - need to match the category ID
                query = query(category__category_id=filters['category'])
            if 'min_price' in filters:
                query = query(price__gte=float(filters['min_price']))  # gte = Greater Than or Equal
            if 'max_price' in filters:
                query = query(price__lte=float(filters['max_price']))  # lte = Less Than or Equal
            if 'brand' in filters:
                query = query(brand__icontains=filters['brand'])  # icontains = Case insensitive search
        
        # Finally, apply pagination and fetch
        docs = query.skip(offset).limit(limit)
        
        # Safety check: old products might have empty categories, so we handle that safely
        return [Product(
            id=d.product_id, name=d.name, description=d.description,
            category_id=d.category.category_id if d.category else None,
            price=d.price, brand=d.brand, quantity=d.quantity
        ) for d in docs]

    def delete(self, product_id: str) -> bool:
        doc = ProductDocument.objects(product_id=product_id).first()
        if doc:
            doc.delete()
            return True
        return False

    def save_many(self, products: List[Product]) -> int:
        # Translate a list of pure Products into a list of Mongo Documents
        docs = []
        for p in products:
            # Fetch the CategoryDocument reference by ID
            category_doc = CategoryDocument.objects(category_id=p.category_id).first() if p.category_id else None
            
            doc = ProductDocument(
                product_id=p.id,
                name=p.name,
                description=p.description,
                category=category_doc,
                price=p.price,
                brand=p.brand,
                quantity=p.quantity
            )
            docs.append(doc)
        
        # .insert() does exactly ONE trip to the database for the entire list!
        if docs:
            ProductDocument.objects.insert(docs)
        
        return len(docs)