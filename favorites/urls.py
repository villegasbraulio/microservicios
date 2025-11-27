from django.urls import path
from . import views

urlpatterns = [
    path('favorites/', views.list_favorites, name='list_favorites'),
    path('favorites/<str:favorite_id>/', views.delete_favorite, name='delete_favorite'),
    path('favorites/product/<str:product_id>/', views.check_favorite, name='check_favorite'),
    path('favorites/admin/popular/', views.get_popular_favorites, name='get_popular_favorites'),
]

