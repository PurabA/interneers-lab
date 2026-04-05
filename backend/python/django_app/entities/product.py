from mongoengine import Document, StringField, FloatField, IntField, DateTimeField, ReferenceField, ValidationError
from datetime import datetime, timezone
from django_app.entities.category import CategoryDocument

def validate_brand_name(brand_name):
    if not brand_name or len(brand_name.strip()) == 0:
        raise ValidationError("Brand cannot be empty.")
    
class ProductDocument(Document):
    meta = {'collection': 'products'}
    
    product_id = StringField(required=True, unique=True)
    name = StringField(required=True)
    description = StringField()
    category = ReferenceField(CategoryDocument)
    price = FloatField(min_value=0)
    brand = StringField(required=True, validation=validate_brand_name)
    quantity = IntField()
    
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super(ProductDocument, self).save(*args, **kwargs)