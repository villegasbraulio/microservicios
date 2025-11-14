from django.urls import path
from . import views

urlpatterns = [
    # Listar favoritos (GET) y crear favorito (POST) - mismo endpoint, diferentes métodos HTTP
    path('favorites/', views.list_favorites, name='list_favorites'),
    path('favorites/<str:favorite_id>/', views.delete_favorite, name='delete_favorite'),  # Cambiado a str para ObjectId
    # Verificar favorito (GET) y eliminar por product_id (DELETE) - mismo endpoint, diferentes métodos HTTP
    path('favorites/product/<str:product_id>/', views.check_favorite, name='check_favorite'),
    path('favorites/stats/', views.get_stats, name='get_stats'),
    path('favorites/admin/popular/', views.get_popular_favorites, name='get_popular_favorites'),
]

