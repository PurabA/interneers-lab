from mongoengine import connect
from django_app.entities.product import ProductDocument
from django_app.entities.category import CategoryDocument
import uuid

def migrate_legacy_data():
    print("🔌 Connecting to MongoDB...")
    connect(host="mongodb://root:example@127.0.0.1:27019/?authSource=admin")

    print("🔍 Scanning for legacy products using raw database access...")
    
    # 1. Get the raw MongoDB collection (Bypasses MongoEngine's strict rules!)
    product_collection = ProductDocument._get_collection()
    
    # 2. Fetch all raw JSON documents
    raw_products = product_collection.find()
    
    fixed_count = 0
    
    for raw_data in raw_products:
        updates = {}
        
        old_category = raw_data.get('category')
        
        
        if isinstance(old_category, str):
            # Create a real Category object for it
            new_cat = CategoryDocument.objects(title=old_category).first()
            if not new_cat:
                new_cat = CategoryDocument(
                    category_id=str(uuid.uuid4()),
                    title=old_category,
                    description=f"Auto-migrated category for {old_category}"
                ).save()
                
            # Tell MongoDB to replace the string with the new real Pointer (ObjectId)
            updates['category'] = new_cat.id
            
        elif old_category is None:
            # If it had no category at all
            default_cat = CategoryDocument.objects(title="Legacy Category").first()
            if not default_cat:
                default_cat = CategoryDocument(category_id=str(uuid.uuid4()), title="Legacy Category").save()
            updates['category'] = default_cat.id

        #  The Brand (Missing -> "Legacy Brand") ---
        old_brand = raw_data.get('brand')
        if not old_brand or str(old_brand).strip() == "":
            updates['brand'] = "Legacy Brand"
            
        # --- APPLY THE FIXES ---
        if updates:
            # Update the document directly in the hard drive
            product_collection.update_one({'_id': raw_data['_id']}, {'$set': updates})
            fixed_count += 1

    print(f"✅ Migration Complete! Cleaned up {fixed_count} legacy products.")

if __name__ == "__main__":
    migrate_legacy_data()