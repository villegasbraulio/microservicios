import requests
from django.conf import settings
from django.http import JsonResponse


class AuthMiddleware:
    """Middleware para validar tokens con el servicio de Auth"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Rutas que no requieren autenticación (solo admin de Django)
        self.exempt_paths = ['/admin/']

    def __call__(self, request):
        # Verificar si la ruta está exenta
        if any(request.path.startswith(path) for path in self.exempt_paths):
            return self.get_response(request)

        # Obtener el token del header Authorization
        # DRF puede envolver el request, así que accedemos al request original
        django_request = request
        if hasattr(request, '_request'):
            django_request = request._request
        
        auth_header = django_request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return JsonResponse(
                {'error': 'Token de autenticación requerido'},
                status=401
            )

        token = auth_header.split(' ')[1] if len(auth_header.split(' ')) > 1 else None
        
        if not token:
            return JsonResponse(
                {'error': 'Token de autenticación inválido'},
                status=401
            )

        # Validar token con el servicio de Auth
        try:
            auth_url = f"{settings.AUTH_SERVICE_URL}/users/current"
            response = requests.get(
                auth_url,
                headers={'Authorization': f'Bearer {token}'},
                timeout=5
            )
            
            if response.status_code != 200:
                return JsonResponse(
                    {'error': 'Token de autenticación inválido o expirado'},
                    status=401
                )
            
            # Obtener información del usuario
            user_data = response.json()
            user_id = user_data.get('id') or user_data.get('_id')
            
            # Asignar user_id tanto al request de Django como al de DRF
            django_request.user_id = user_id
            django_request.user_data = user_data
            if hasattr(request, '_request'):
                request.user_id = user_id
                request.user_data = user_data
            
        except requests.exceptions.RequestException as e:
            return JsonResponse(
                {'error': f'Error al validar token: {str(e)}'},
                status=503
            )

        return self.get_response(request)

