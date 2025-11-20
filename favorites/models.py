from pymongo import MongoClient
from django.conf import settings
from datetime import datetime


def get_mongo_client():
    return MongoClient(settings.MONGODB_HOST)


def get_favorites_collection():
    client = get_mongo_client()
    db = client[settings.MONGODB_NAME]
    collection = db['favorites']
    collection.create_index([('user_id', 1), ('product_id', 1)], unique=True)
    collection.create_index([('user_id', 1)])
    collection.create_index([('product_id', 1)])
    return collection


class Favorite:
    def __init__(self, product_id, user_id, notes=None, created_at=None, updated_at=None, _id=None):
        self._id = _id
        self.product_id = product_id
        self.user_id = user_id
        self.notes = notes or ''
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': str(self._id) if self._id else None,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else str(self.created_at),
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else str(self.updated_at),
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            _id=data.get('_id'),
            product_id=data.get('product_id'),
            user_id=data.get('user_id'),
            notes=data.get('notes', ''),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

