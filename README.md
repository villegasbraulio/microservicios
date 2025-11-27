# Microservicio de Favoritos (Django)

Microservicio para gestionar la lista de favoritos de los usuarios.

## Requisitos Previos

1. **Python 3.11 o superior** instalado
2. **MongoDB** corriendo en `localhost:27017`
3. **RabbitMQ** corriendo en `amqp://guest:guest@localhost:5672/` (puedes levantarlo con Docker `-p 5672:5672 -p 15672:15672 rabbitmq:3.11-management`)
4. **Servicio de Auth** corriendo en `http://localhost:3000`

## Instalación y Configuración

### 1. Crear entorno virtual (recomendado)

```bash
cd favorites-django
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

El servicio usa las siguientes variables de entorno (opcionales, tienen valores por defecto):

```bash
export MONGODB_HOST=mongodb://localhost:27017/
export MONGODB_NAME=favorites_db
export RABBIT_URL=amqp://guest:guest@localhost:5672/
export AUTH_SERVICE_URL=http://localhost:3000
export DJANGO_SETTINGS_MODULE=core.settings
```

### 4. Ejecutar migraciones (opcional para MongoDB)

MongoDB con djongo no requiere migraciones tradicionales, pero puedes ejecutar:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Iniciar el servidor de desarrollo

```bash
python manage.py runserver 0.0.0.0:3006
```

O usar el script automatizado:

```bash
./run-local.sh
```

## API Endpoints

### Obtener favoritos del usuario
```
GET /api/favorites/?page=1&limit=20
Authorization: Bearer <token>
```

### Verificar si un producto está en favoritos
```
GET /api/favorites/product/<product_id>/
Authorization: Bearer <token>
```

### Agregar un favorito
```
POST /api/favorites/
Authorization: Bearer <token>
Content-Type: application/json

{
  "product_id": "PRODUCT_ID",
  "notes": "Nota opcional"
}
```

### Eliminar un favorito por ID
```
DELETE /api/favorites/<favorite_id>/
Authorization: Bearer <token>
```

### Eliminar un favorito por product_id
```
DELETE /api/favorites/product/<product_id>/
Authorization: Bearer <token>
```

### Obtener productos más populares (admin)
```
GET /api/favorites/admin/popular/?limit=10
Authorization: Bearer <token>
```

## Verificar que funciona

Una vez iniciado, el servicio estará disponible en:
- **REST API**: http://localhost:3006/api/
- **Admin Panel**: http://localhost:3006/admin/ (requiere crear superusuario)

### Probar la API

```bash
# Obtener favoritos (necesita token válido)
curl -H "Authorization: Bearer TU_TOKEN" \
  http://localhost:3006/api/favorites/

# Verificar si un producto está en favoritos
curl -H "Authorization: Bearer TU_TOKEN" \
  http://localhost:3006/api/favorites/product/PRODUCT_ID/

# Agregar un favorito
curl -X POST \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id": "PRODUCT_ID", "notes": "Nota opcional"}' \
  http://localhost:3006/api/favorites/
```

## Solución de Problemas

### MongoDB no está corriendo

```bash
# Iniciar MongoDB con Docker
docker run -d --name ec-mongo -p 27017:27017 mongo:6.0
```

### Servicio de Auth no está corriendo

Asegúrate de que el servicio de Auth esté corriendo en el puerto 3000:

```bash
# Verificar que el servicio de Auth responda
curl http://localhost:3000/users/current -H "Authorization: Bearer test"
```

### Error de conexión a Auth Service

Si el servicio de Auth está en Docker y el servicio de Favorites está corriendo localmente, 
necesitas usar `host.docker.internal` solo si estás en Mac/Windows. En Linux, usa la IP del host.

Para desarrollo local, ambos servicios deben estar en la misma máquina, así que `localhost` debería funcionar.

### Error de permisos en MongoDB

Si MongoDB requiere autenticación, configura las variables de entorno:

```bash
export MONGODB_USER=tu_usuario
export MONGODB_PASSWORD=tu_password
export MONGODB_AUTH_SOURCE=admin
```

## Desarrollo

Para desarrollo, Django tiene recarga automática. Solo guarda los archivos y el servidor se recargará automáticamente.

Para ver logs detallados, ejecuta:

```bash
python manage.py runserver 0.0.0.0:3006 --verbosity 2
```

