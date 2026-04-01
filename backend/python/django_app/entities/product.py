from mongoengine import Document, StringField, FloatField, IntField, DateTimeField
from datetime import datetime, timezone

class ProductDocument(Document):
    meta = {'collection': 'products'}
    
    product_id = StringField(required=True, unique=True)
    name = StringField(required=True)
    description = StringField()
    category = StringField()
    price = FloatField()
    brand = StringField()
    quantity = IntField()
    
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super(ProductDocument, self).save(*args, **kwargs)