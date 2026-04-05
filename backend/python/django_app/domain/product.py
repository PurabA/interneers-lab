from dataclasses import dataclass
import uuid

@dataclass
class Product:
    # We use a unique ID for every product so we can easily find/update/delete it later using this ID
    id: str 
    name: str
    description: str
    category_id: str
    price: float
    brand: str
    quantity: int

    # This is a helper method to easily create a brand new product with a random ID
    @classmethod
    def create_new(cls, name, description, category_id, price, brand, quantity):
        return cls(
            id=str(uuid.uuid4()), # Generates a random unique ID
            name=name,
            description=description,
            category_id=category_id,
            price=price,
            brand=brand,
            quantity=quantity
        )