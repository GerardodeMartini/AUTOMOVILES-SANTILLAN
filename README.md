# Automóviles Santillán - Plataforma Web y Catálogo de Vehículos

Proyecto Django desarrollado para la concesionaria **Automóviles Santillán**, utilizando **Bootstrap 5** en el frontend, **PostgreSQL** como motor de base de datos relacional y un **Panel de Configuración HTML a medida** para la administración de vehículos.

---

## 🚀 Características Principales

1. **Catálogo Público de Vehículos (`/`):**
   - **Header Fijo:** Nombre de la concesionaria a la izquierda, líneas de atención y botones de WhatsApp a la derecha, más acceso directo a **Configuración**.
   - **Botonera de Categorías:** Filtrado dinámico por *Pick up, Hatchback, Sedan, Utilitario, 7 asientos* con botón "Todas".
   - **Cards de Bootstrap:** Vista resumida de cada unidad con foto principal, badges de año y categoría, lista técnica (Marca, Modelo, Año, Motor, Transmisión, Tracción, Combustible) y botón **"Ver más detalles"**.
   - **Vista de Detalle (`/vehiculo/<id>/`):** Carrusel de Bootstrap 5 con **rotación automática**, ficha técnica exhaustiva, descripción detallada y botón para consultar por WhatsApp con mensaje pre-cargado.

2. **Panel de Configuración HTML a Medida (`/panel/`):**
   - **Autenticación Estricta:** Pantalla de login personalizada con Bootstrap 5 (`/panel/login/`) que exige credenciales de **Superusuario / Administrador**.
   - **Dashboard Administrativo:** Estadísticas de stock en tiempo real (total, visibles, pausados), buscador y listado completo de unidades.
   - **Carga de Vehículos (`/panel/vehiculo/nuevo/`):** Formulario intuitivo con carga múltiple de **hasta 20 fotografías** simultáneas.
   - **Edición y Galería (`/panel/vehiculo/<id>/editar/`):** Modificación de datos y administración visual de fotos existentes, con borrado individual y contador de cupo restante.
   - **Toggle Rápido:** Publicar o pausar vehículos con un solo clic.
   - **Eliminación Segura (`/panel/vehiculo/<id>/eliminar/`):** Pantalla de confirmación con detalle de fotos asociadas antes de borrar.

3. **Base de Datos y Multimedia:**
   - Soporte para **PostgreSQL** (`django.db.backends.postgresql`) configurado con variables de entorno (`django-environ`).
   - Configuración de `MEDIA_URL` y `MEDIA_ROOT` para la subida y entrega de fotografías.

4. **Poblado Rápido de Datos:**
   - Comando `python manage.py poblar_catalogo`: Crea la **Chevrolet S10 2004** con 3 imágenes de prueba generadas dinámicamente con Pillow.
   - Comando `python manage.py crear_superusuario`: Genera el usuario administrador por defecto (`admin` / `admin`).

---

## 🛠 Instalación y Puesta en Marcha

### 1. Requisitos Previos
- Python 3.10 o superior
- PostgreSQL (opcionalmente SQLite para pruebas locales inmediatas)

### 2. Dependencias
```bash
pip install -r requirements.txt
```

### 3. Variables de Entorno (`.env`)
Configura tu conexión a PostgreSQL en el archivo `.env`:
```env
DEBUG=True
SECRET_KEY=django-insecure-santillan-change-in-production-key-xyz123
ALLOWED_HOSTS=localhost,127.0.0.1,*

# Cambiar a False para usar PostgreSQL
USE_SQLITE=False

# Conexión PostgreSQL
DATABASE_URL=postgres://usuario:contraseña@localhost:5432/santillan_db
DB_NAME=santillan_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### 4. Migraciones y Carga Inicial
```bash
python manage.py makemigrations catalogo
python manage.py migrate
python manage.py crear_superusuario
python manage.py poblar_catalogo
```

### 5. Iniciar el Servidor
```bash
python manage.py runserver
```

---

## 🌐 URLs Principales

| Vista | URL | Descripción |
|---|---|---|
| **Catálogo Público** | `http://127.0.0.1:8000/` | Catálogo de autos para clientes con filtros |
| **Detalle de Unidad** | `http://127.0.0.1:8000/vehiculo/<id>/` | Ficha técnica y carrusel automático de fotos |
| **Panel de Configuración** | `http://127.0.0.1:8000/panel/` | Dashboard administrativo de vehículos |
| **Login del Panel** | `http://127.0.0.1:8000/panel/login/` | Autenticación de Superusuario (`admin` / `admin`) |
| **Nuevo Vehículo** | `http://127.0.0.1:8000/panel/vehiculo/nuevo/` | Formulario con subida múltiple (hasta 20 fotos) |
