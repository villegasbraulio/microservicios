# Modelo usando pymongo directamente - no usamos Django ORM para MongoDB
# Este archivo se mantiene para compatibilidad con admin, pero usamos pymongo en las vistas
from pymongo import MongoClient
from django.conf import settings
from datetime import datetime
from bson import ObjectId


def get_mongo_client():
    """Obtener cliente de MongoDB"""
    return MongoClient(settings.MONGODB_HOST)


def get_favorites_collection():
    """Obtener colección de favoritos"""
    client = get_mongo_client()
    db = client[settings.MONGODB_NAME]
    collection = db['favorites']
    # Crear índices si no existen
    collection.create_index([('user_id', 1), ('product_id', 1)], unique=True)
    collection.create_index([('user_id', 1)])
    collection.create_index([('product_id', 1)])
    return collection


class Favorite:
    """Clase para representar un favorito"""
    def __init__(self, product_id, user_id, notes=None, created_at=None, updated_at=None, _id=None):
        self._id = _id
        self.product_id = product_id
        self.user_id = user_id
        self.notes = notes or ''
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        result = {
            'id': str(self._id) if self._id else None,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else str(self.created_at),
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else str(self.updated_at),
        }
        return result
    
    @classmethod
    def from_dict(cls, data):
        """Crear instancia desde diccionario de MongoDB"""
        return cls(
            _id=data.get('_id'),
            product_id=data.get('product_id'),
            user_id=data.get('user_id'),
            notes=data.get('notes', ''),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

