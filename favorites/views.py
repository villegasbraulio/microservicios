from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta, datetime
from .models import get_favorites_collection, Favorite
from .serializers import FavoriteSerializer, FavoriteCreateSerializer, FavoriteCheckSerializer


@api_view(['GET', 'POST'])
def list_favorites(request):
    """Obtener todos los favoritos del usuario autenticado (GET) o crear uno nuevo (POST)"""
    if request.method == 'POST':
        # Llamar directamente a la lógica de create_favorite en lugar de llamar a la función
        # para evitar problemas con el wrapper de DRF
        user_id = request.user_id
        collection = get_favorites_collection()
        
        serializer = FavoriteCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        product_id = serializer.validated_data['product_id']
        notes = serializer.validated_data.get('notes', '')
        
        # Verificar si ya existe
        existing = collection.find_one({'user_id': user_id, 'product_id': product_id})
        
        if existing:
            # Actualizar notas si ya existe
            if notes:
                collection.update_one(
                    {'_id': existing['_id']},
                    {'$set': {'notes': notes, 'updated_at': datetime.utcnow()}}
                )
                existing['notes'] = notes
                existing['updated_at'] = datetime.utcnow()
            favorite = Favorite.from_dict(existing)
            return Response(favorite.to_dict(), status=status.HTTP_200_OK)
        else:
            # Crear nuevo favorito
            now = datetime.utcnow()
            favorite_doc = {
                'user_id': user_id,
                'product_id': product_id,
                'notes': notes,
                'created_at': now,
                'updated_at': now
            }
            result = collection.insert_one(favorite_doc)
            favorite_doc['_id'] = result.inserted_id
            favorite = Favorite.from_dict(favorite_doc)
            return Response(favorite.to_dict(), status=status.HTTP_201_CREATED)
    
    user_id = request.user_id
    collection = get_favorites_collection()
    
    # Paginación
    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 20))
    skip = (page - 1) * limit
    
    # Obtener favoritos
    favorites_cursor = collection.find({'user_id': user_id}).sort('created_at', -1).skip(skip).limit(limit)
    favorites = [Favorite.from_dict(fav) for fav in favorites_cursor]
    
    # Contar total
    total_count = collection.count_documents({'user_id': user_id})
    total_pages = (total_count + limit - 1) // limit if limit > 0 else 1
    
    # Serializar
    favorites_data = [fav.to_dict() for fav in favorites]
    
    return Response({
        'results': favorites_data,
        'count': total_count,
        'page': page,
        'limit': limit,
        'total_pages': total_pages,
    })


@api_view(['GET', 'DELETE'])
def check_favorite(request, product_id):
    """Verificar si un producto está en favoritos del usuario (GET) o eliminarlo (DELETE)"""
    if request.method == 'DELETE':
        # Llamar directamente a la lógica en lugar de la función
        user_id = request.user_id
        collection = get_favorites_collection()
        
        result = collection.delete_one({'user_id': user_id, 'product_id': product_id})
        if result.deleted_count > 0:
            return Response({'message': 'Favorito eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'Favorito no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    user_id = request.user_id
    collection = get_favorites_collection()
    
    favorite_doc = collection.find_one({'user_id': user_id, 'product_id': product_id})
    
    if favorite_doc:
        favorite = Favorite.from_dict(favorite_doc)
        return Response({
            'is_favorite': True,
            'favorite': favorite.to_dict()
        })
    else:
        return Response({
            'is_favorite': False
        })


@api_view(['POST'])
def create_favorite(request):
    """Agregar un producto a favoritos"""
    user_id = request.user_id
    collection = get_favorites_collection()
    
    serializer = FavoriteCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    product_id = serializer.validated_data['product_id']
    notes = serializer.validated_data.get('notes', '')
    
    # Verificar si ya existe
    existing = collection.find_one({'user_id': user_id, 'product_id': product_id})
    
    if existing:
        # Actualizar notas si ya existe
        if notes:
            collection.update_one(
                {'_id': existing['_id']},
                {'$set': {'notes': notes, 'updated_at': datetime.utcnow()}}
            )
            existing['notes'] = notes
            existing['updated_at'] = datetime.utcnow()
        favorite = Favorite.from_dict(existing)
        return Response(favorite.to_dict(), status=status.HTTP_200_OK)
    else:
        # Crear nuevo favorito
        now = datetime.utcnow()
        favorite_doc = {
            'user_id': user_id,
            'product_id': product_id,
            'notes': notes,
            'created_at': now,
            'updated_at': now
        }
        result = collection.insert_one(favorite_doc)
        favorite_doc['_id'] = result.inserted_id
        favorite = Favorite.from_dict(favorite_doc)
        return Response(favorite.to_dict(), status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def delete_favorite(request, favorite_id):
    """Eliminar un favorito por ID"""
    user_id = request.user_id
    collection = get_favorites_collection()
    
    try:
        from bson import ObjectId
        result = collection.delete_one({'_id': ObjectId(favorite_id), 'user_id': user_id})
        if result.deleted_count > 0:
            return Response({'message': 'Favorito eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'Favorito no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'Error al eliminar favorito: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_favorite_by_product(request, product_id):
    """Eliminar un favorito por product_id"""
    user_id = request.user_id
    collection = get_favorites_collection()
    
    result = collection.delete_one({'user_id': user_id, 'product_id': product_id})
    if result.deleted_count > 0:
        return Response({'message': 'Favorito eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)
    else:
        return Response({'error': 'Favorito no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_stats(request):
    """Obtener estadísticas de favoritos del usuario"""
    user_id = request.user_id
    collection = get_favorites_collection()
    
    total_favorites = collection.count_documents({'user_id': user_id})
    
    # Favoritos agregados en los últimos 30 días
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_count = collection.count_documents({
        'user_id': user_id,
        'created_at': {'$gte': thirty_days_ago}
    })
    
    # Favoritos más recientes (últimos 5)
    most_recent_cursor = collection.find({'user_id': user_id}).sort('created_at', -1).limit(5)
    most_recent = [
        {
            'product_id': fav.get('product_id'),
            'created_at': fav.get('created_at').isoformat() if isinstance(fav.get('created_at'), datetime) else str(fav.get('created_at'))
        }
        for fav in most_recent_cursor
    ]
    
    return Response({
        'total_favorites': total_favorites,
        'recent_count': recent_count,
        'most_recent': most_recent
    })


@api_view(['GET'])
def get_popular_favorites(request):
    """Obtener productos más populares (más veces agregados a favoritos) - Solo admin"""
    limit = int(request.query_params.get('limit', 10))
    collection = get_favorites_collection()
    
    # Agrupar por product_id y contar usando aggregation
    pipeline = [
        {'$group': {
            '_id': '$product_id',
            'favorite_count': {'$sum': 1},
            'last_added': {'$max': '$created_at'}
        }},
        {'$sort': {'favorite_count': -1}},
        {'$limit': limit}
    ]
    
    popular = list(collection.aggregate(pipeline))
    
    result = [
        {
            'product_id': item['_id'],
            'favorite_count': item['favorite_count'],
            'last_added': item['last_added'].isoformat() if isinstance(item.get('last_added'), datetime) else str(item.get('last_added', ''))
        }
        for item in popular
    ]
    
    return Response({
        'popular_products': result
    })
