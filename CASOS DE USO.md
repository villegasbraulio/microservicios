# Arquitectura del Microservicio de Favoritos

## Descripción General

Microservicio REST desarrollado en Django que gestiona la lista de favoritos (wishlist) de los usuarios en un sistema de e-commerce. Permite a los usuarios autenticados guardar productos del catálogo en una lista personal para revisarlos o comprarlos posteriormente.

## Stack Tecnológico

- **Framework**: Django 4.2.7
- **API REST**: Django REST Framework 3.14.0
- **Base de Datos**: MongoDB (acceso directo con PyMongo)
- **Autenticación**: Integración con servicio de Auth externo mediante middleware
- **CORS**: django-cors-headers para permitir peticiones desde el frontend

## Modelo de Datos

### Entidad: Favorite

```python
{
    "_id": ObjectId,              # Identificador único de MongoDB
    "user_id": String,             # ID del usuario (obtenido del servicio de Auth)
    "product_id": String,          # ID del producto del catálogo
    "notes": String,               # Notas opcionales del usuario
    "created_at": DateTime,        # Fecha de creación
    "updated_at": DateTime         # Fecha de última actualización
}
```

### Índices MongoDB

- **Índice único compuesto**: `(user_id, product_id)` - Previene duplicados
- **Índice simple**: `user_id` - Optimiza consultas por usuario
- **Índice simple**: `product_id` - Optimiza consultas por producto

## Arquitectura del Sistema

### Componentes Principales

1. **Middleware de Autenticación** (`favorites/middleware.py`)
   - Valida tokens JWT con el servicio de Auth
   - Extrae `user_id` del token y lo adjunta al request
   - Protege todas las rutas excepto `/admin/`

2. **Modelo de Datos** (`favorites/models.py`)
   - Clase `Favorite` para representar favoritos
   - Funciones de acceso a MongoDB (`get_favorites_collection`)
   - Métodos de serialización (`to_dict`, `from_dict`)

3. **Vistas REST** (`favorites/views.py`)
   - Endpoints para CRUD de favoritos
   - Lógica de negocio y validaciones
   - Integración directa con MongoDB mediante PyMongo

4. **Serializers** (`favorites/serializers.py`)
   - Validación de datos de entrada
   - Serialización de respuestas JSON

## Endpoints de la API

### 1. Listar Favoritos
- **GET** `/api/favorites/?page=1&limit=20`
- **Respuesta**: Lista paginada de favoritos del usuario autenticado
- **Autenticación**: Requerida

### 2. Crear Favorito
- **POST** `/api/favorites/`
- **Body**: `{"product_id": "string", "notes": "string (opcional)"}`
- **Respuesta**: Favorito creado o actualizado (si ya existe)
- **Autenticación**: Requerida

### 3. Verificar Favorito
- **GET** `/api/favorites/product/<product_id>/`
- **Respuesta**: `{"is_favorite": boolean, "favorite": {...}}`
- **Autenticación**: Requerida

### 4. Eliminar Favorito por Product ID
- **DELETE** `/api/favorites/product/<product_id>/`
- **Respuesta**: 204 No Content
- **Autenticación**: Requerida

### 5. Eliminar Favorito por ID
- **DELETE** `/api/favorites/<favorite_id>/`
- **Respuesta**: 204 No Content
- **Autenticación**: Requerida

### 6. Estadísticas del Usuario
- **GET** `/api/favorites/stats/`
- **Respuesta**: Total de favoritos, favoritos recientes (30 días), últimos 5 agregados
- **Autenticación**: Requerida

### 7. Productos Populares (Admin)
- **GET** `/api/favorites/admin/popular/?limit=10`
- **Respuesta**: Productos más agregados a favoritos
- **Autenticación**: Requerida

## Flujo de Autenticación

1. Cliente envía petición con header `Authorization: Bearer <token>`
2. `AuthMiddleware` intercepta la petición
3. Middleware valida token con servicio de Auth (`http://localhost:3000/users/current`)
4. Si el token es válido, extrae `user_id` y lo adjunta al request
5. Vista procesa la petición con `request.user_id` disponible
6. Si el token es inválido, retorna 401 Unauthorized

## Casos de Uso que Complementa

### 1. Gestión de Lista de Deseos
- **Actor**: Usuario autenticado
- **Flujo**: 
  - Usuario navega catálogo → Ve producto interesante → Agrega a favoritos
  - Usuario puede ver su lista de favoritos → Revisa productos guardados
  - Usuario puede eliminar productos de favoritos
- **Beneficio**: Mejora experiencia de usuario, facilita compras futuras

### 2. Verificación de Estado de Favorito
- **Actor**: Frontend/UI
- **Flujo**: 
  - Al mostrar lista de productos, verifica si cada uno está en favoritos
  - Muestra indicador visual (corazón lleno/vacío) según estado
- **Beneficio**: Feedback visual inmediato al usuario

### 3. Análisis de Engagement
- **Actor**: Administrador
- **Flujo**: 
  - Consulta productos más populares (más veces agregados a favoritos)
  - Analiza estadísticas de uso de favoritos
- **Beneficio**: Métricas de negocio, identificación de productos de interés

### 4. Personalización de Experiencia
- **Actor**: Sistema
- **Flujo**: 
  - Sistema puede usar historial de favoritos para recomendaciones
  - Notificaciones sobre descuentos en productos favoritos
- **Beneficio**: Mayor conversión, mejor experiencia personalizada

## Integración con Otros Microservicios

### Servicio de Autenticación
- **Endpoint**: `http://localhost:3000/users/current`
- **Propósito**: Validación de tokens JWT
- **Método**: GET con header Authorization

### Servicio de Catálogo
- **Integración**: Indirecta (el frontend consulta catálogo para mostrar detalles)
- **Datos compartidos**: `product_id` hace referencia a productos del catálogo

## Características Técnicas

### Seguridad
- Validación de tokens en cada petición
- Aislamiento de datos por usuario (`user_id`)
- Prevención de duplicados mediante índice único
- CORS configurado para orígenes específicos

### Rendimiento
- Índices MongoDB optimizados para consultas frecuentes
- Paginación en listado de favoritos
- Agregaciones MongoDB para estadísticas

### Escalabilidad
- Acceso directo a MongoDB (sin ORM overhead)
- Arquitectura stateless (sin sesiones)
- Preparado para despliegue en contenedores

## Consideraciones de Diseño

1. **No se valida existencia del producto**: El microservicio confía en que el `product_id` existe en el catálogo
2. **Idempotencia**: Agregar el mismo producto múltiples veces no crea duplicados (índice único)
3. **Soft delete**: No implementado - eliminación es permanente
4. **Eventos**: No se publican eventos a RabbitMQ (puede agregarse para notificaciones)

## Dependencias Externas

- **MongoDB**: Base de datos NoSQL para almacenamiento
- **Servicio de Auth**: Validación de autenticación
- **Frontend React**: Cliente que consume la API

## Configuración

Variables de entorno:
- `MONGODB_HOST`: URL de conexión a MongoDB (default: `mongodb://localhost:27017/`)
- `MONGODB_NAME`: Nombre de la base de datos (default: `favorites_db`)
- `AUTH_SERVICE_URL`: URL del servicio de autenticación (default: `http://localhost:3000`)
- `SECRET_KEY`: Clave secreta de Django
- `DEBUG`: Modo debug (default: `True`)

