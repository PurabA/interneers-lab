from mongoengine import Document, StringField

class CategoryDocument(Document):
    # This creates a new collection in MongoDB called 'categories'
    meta = {'collection': 'categories'}
    
    category_id = StringField(required=True, unique=True)
    title = StringField(required=True, unique=True)
    description = StringField()