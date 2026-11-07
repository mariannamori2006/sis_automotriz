# Automotriz Profesional — Django + MariaDB

Proyecto educativo completo, basado en la estructura de Agenda Simple (`config/`, `control/`, `templates/control/`, `static/control/`).

**Siete tablas de negocio:** `cita`, `cliente`, `diagnostico`, `mecanico`, `ordenServicio`, `repuesto`, `vehiculo`. Django crea además tablas internas para usuarios, permisos y sesiones.

## Instalación en Windows (PowerShell)

1. Descomprimir el proyecto en `C:\xampp\htdocs` (o cualquier otra carpeta). XAMPP solo sirve para MariaDB; Django se ejecuta con su propio servidor.
2. Crear el entorno: `py -m venv .venv`.
3. Instalar dependencias sin activar el entorno: `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`.
4. Copiar `.env.example` como `.env`; completar los datos reales de MariaDB, especialmente `DB_PORT` (en muchos equipos es 3306; en tu Agenda Simple era 3307).
5. En phpMyAdmin, ejecutar el SQL incluido en `database/crear_bd.sql`.
6. Migrar: `.\.venv\Scripts\python.exe manage.py migrate`.
7. Administrador: `.\.venv\Scripts\python.exe manage.py createsuperuser`.
8. Iniciar: `.\.venv\Scripts\python.exe manage.py runserver`.
9. Abrir `http://127.0.0.1:8000/login/`.

> Nunca reutilices ni copies la carpeta `.venv` entre equipos. Crea un entorno nuevo en cada PC.

## Despliegue en hosting (Linux con Python y MariaDB)

1. Contrata hosting **compatible con aplicaciones WSGI/ASGI Python**, MariaDB 10.5+ y HTTPS; no basta un hosting PHP/XAMPP estándar.
2. Instala `requirements.txt` y configura variables `.env`: `DJANGO_DEBUG=0`, una `DJANGO_SECRET_KEY` aleatoria y secreta, `DJANGO_ALLOWED_HOSTS=tudominio.com`, `DJANGO_CSRF_TRUSTED_ORIGINS=https://tudominio.com`, `DB_*` reales y `REGISTRATION_CODE` secreto.
3. Ejecuta `python manage.py migrate`, `python manage.py collectstatic --noinput`, `python manage.py check --deploy`.
4. Configura la aplicación WSGI (`config.wsgi:application`) mediante Gunicorn/uWSGI o el panel del proveedor y proxy inverso con HTTPS. En plataformas tras proxy, configura `SECURE_PROXY_SSL_HEADER` **solo cuando** el proveedor elimina y establece correctamente ese encabezado.
5. Implementa respaldos cifrados de la base de datos, control de acceso por puesto, retención de datos, consentimiento, registro de accesos y plan de recuperación antes de almacenar historias clínicas reales.
6. Antes de abrir registro al público: en producción solo se permite alta con el código de invitación `REGISTRATION_CODE`. Si está vacío, el registro se deshabilita. Para cerrar altas luego, borra `REGISTRATION_CODE` y reinicia la aplicación.

**Limitación deliberada de esta versión:** todos los usuarios autenticados pueden ver y modificar registros; para una clínica con varios roles o sucursales se requiere autorización granular, auditoría, políticas de privacidad y revisión de seguridad antes de considerarla apta para datos clínicos reales. Las recetas contienen un medicamento por registro; para varios medicamentos se crean varias recetas vinculadas al mismo diagnóstico.

## Reportes

- `/reportes/citas/`: citas filtradas por rango de fechas y estado, imprimibles.
- En las listas de citas, diagnósticos y recetas: acción **Imprimir**.
- En la ventana de impresión puedes seleccionar **Guardar como PDF** en el navegador.

## Pruebas

`python manage.py test apps`

## Orden de registros recomendado

Cliente → Vehiculo → Mecanico → Orden servicio → Citas → Diagnósticos → Repuesto.

## Documentación

Leer `MANUAL_DEL_PROFESOR.md`.

## Organización de modelos y tipografía (actualización)

Las clases están separadas en `control/models/`: `Cita.py`, `Cliente.py`, `Diagnostico.py`, `Mecanico.py`, `OrdenServicio.py`, `Repuesto.py` y `Vehiculo.py`. `control/models/__init__.py` las registra mediante importaciones. El texto estándar y los controles se muestran con letra de 16 px. **No se necesita borrar ni volver a crear la base de datos:** la migración inicial conserva la misma estructura.
