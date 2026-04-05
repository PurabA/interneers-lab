from dataclasses import dataclass
import uuid

@dataclass
class ProductCategory:
    id: str
    title: str
    description: str

    @classmethod
    def create_new(cls, title: str, description: str = ""):
        return cls(
            id=str(uuid.uuid4()), 
            title=title, 
            description=description
        )