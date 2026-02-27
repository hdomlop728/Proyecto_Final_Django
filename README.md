# InvoiceRPG — Documentación del proyecto

## ¿Qué es esto?

InvoiceRPG es una plataforma de gestión para freelancers. La idea es simple: un freelancer
puede gestionar sus clientes, crear proyectos para ellos, generar presupuestos y convertirlos
en facturas cuando el cliente los acepta. También puede registrar los pagos que va recibiendo
y ver en el dashboard un resumen de todo lo que ha facturado, cobrado y tiene pendiente.

Los clientes también pueden registrarse y tener acceso limitado para ver sus propios proyectos,
presupuestos y facturas, pero no pueden tocar nada, solo consultar.

---

## Tecnologías usadas

- **Django 6.0.2** como framework principal
- **PostgreSQL** como base de datos
- **Python 3.12**
- **Bootstrap 5** para el frontend
- **Docker** para levantar el entorno completo sin instalar nada manualmente

---

## Estructura del proyecto

El proyecto tiene 6 apps dentro de la carpeta `apps/`:

- **usuarios** — gestiona el registro, login y el perfil de cada usuario
- **clientes** — CRUD de clientes del freelancer
- **proyectos** — CRUD de proyectos asociados a clientes
- **presupuestos** — CRUD de presupuestos y conversión a factura
- **facturas** — gestión de facturas y registro de pagos
- **setup** — app de infraestructura: grupos, permisos, mixins y middleware

---

## Cómo levantar el proyecto en local (sin Docker)

**1. Clona el repositorio**
```
git clone https://github.com/hdomlop728/Proyecto_Final_Django.git
cd Proyecto_Final_Django
```

**2. Crea y activa el entorno virtual**
```
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows
```

**3. Instala las dependencias**
```
pip install -r requirements.txt
```

**4. Crea el archivo .env en la raíz del proyecto**
Crea un archivo llamado `.env` con los siguientes valores:
```
SECRET_KEY='django-insecure-h8%q0i5)-2!nq82cevzgw4o9(h3u-=nu97ydgyzf0sp%-t@iz3'
DB_NAME=invoicerpg
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

**5. Configura PostgreSQL**
```
sudo apt install postgresql postgresql-contrib
sudo -u postgres psql
CREATE DATABASE invoicerpg;
ALTER USER postgres WITH PASSWORD 'postgres';
\q
```

**6. Aplica las migraciones**
```
python manage.py migrate
```

**7. Crea el superusuario**
```
python manage.py createsuperuser
```
Los datos del superusuario por defecto son: usuario `admin`, email `admin@gmail.com`, contraseña `admin`

**8. Arranca el servidor**
```
python manage.py runserver
```

La web estará en http://127.0.0.1:8000

---

## Cómo levantar el proyecto con Docker

Si no quieres instalar PostgreSQL manualmente, Docker levanta todo de golpe.

**1. Asegúrate de tener Docker instalado**

**2. Crea el archivo .env** igual que en el paso 4 de arriba

**3. Construye y levanta los contenedores**
```
docker compose up --build
```

**4. En otra terminal, aplica las migraciones**
```
docker compose exec web python manage.py migrate
```

**5. Crea el superusuario**
```
docker compose exec web python manage.py createsuperuser
```

La web estará en http://localhost:8000 igual que en local.

Para parar Docker:
```
docker compose down
```

Los datos de PostgreSQL se guardan en un volumen y no se pierden aunque pares los contenedores.

---

## Tipos de usuario y permisos

Hay dos tipos de cuenta:

**FREELANCER**
- Puede hacer todo: crear y gestionar clientes, proyectos, presupuestos y facturas
- Puede convertir presupuestos a facturas y registrar pagos
- Solo ve sus propios datos, nunca los de otro freelancer

**CLIENTE**
- Solo puede ver (no crear ni editar) los proyectos, presupuestos y facturas que le corresponden
- No tiene acceso a los datos de otros clientes

Los grupos y sus permisos se crean automáticamente al hacer `migrate` gracias a la migración
de la app `setup`. No hace falta configurar nada a mano.

---

## Modelos principales

**Usuario** — extiende AbstractUser de Django, añade email único como identificador

**Perfil** — vinculado 1 a 1 con Usuario, guarda el tipo de cuenta (freelancer/cliente),
datos fiscales (NIF/CIF) y preferencias de interfaz (tema, idioma, formato de números)

**Cliente** — pertenece a un freelancer, puede tener un usuario asociado si se registra en la plataforma

**Proyecto** — pertenece a un cliente y a un freelancer, tiene estados: activo, pausado, finalizado

**Presupuesto** — pertenece a un proyecto, genera automáticamente un número de serie (YYYY-NNN),
se puede convertir a factura si está aceptado

**Factura** — se crea a partir de un presupuesto, guarda los pagos en un JSONField y
actualiza el total cobrado usando F expressions para no hacer cálculos en Python

---

## Decisiones técnicas relevantes

**¿Por qué AbstractUser y no AbstractBaseUser?**
AbstractUser ya trae todo lo necesario (username, email, is_active...). Solo necesitábamos
añadir email único, así que no tenía sentido reimplementar todo desde cero.

**¿Por qué JSONField para los pagos en vez de un modelo aparte?**
El enunciado pedía una relación ManyToMany. Elegimos el JSONField como alternativa porque
evita crear un séptimo modelo y permite registrar varios pagos por factura. Para poder
hacer consultas ORM sobre el total cobrado, añadimos el campo `total_pagado` que se
actualiza automáticamente con F expressions cada vez que se registra un pago.

**¿Por qué on_delete=PROTECT en las claves foráneas?**
Para evitar borrados en cascada accidentales. Si intentas borrar un cliente que tiene
proyectos, Django te lo impide. Mismo comportamiento en proyectos con presupuestos y
en presupuestos con facturas, manteniendo así la trazabilidad de todo el flujo.

**¿Por qué el middleware va al final del MIDDLEWARE en settings.py?**
El AuditoriaMiddleware necesita saber quién es el usuario para registrarlo en el log.
Si va antes que AuthenticationMiddleware, request.user todavía no existe y registraría
todo como "anonimo". Al ir al final, todos los middlewares anteriores ya han procesado
la petición y request.user está disponible.

---

## Workflow del equipo

Trabajamos con Git y GitHub los tres, sobre la rama `main` directamente. No usamos ramas
separadas, nos coordinamos hablando para no pisar el trabajo de los demás y haciendo pull
antes de cada push. Cuando hubo algún conflicto se resolvió en el momento entre los
implicados.

El reparto quedó así:

**Héctor** se encargó de todo lo relacionado con seguridad y flujos: el usuario personalizado,
los grupos FREELANCER y CLIENTE con sus permisos, los signals, los mixins, los formularios
con sus validaciones y toda la parte de autenticación.

**Jaime** se encargó de la infraestructura y la documentación: las vistas CRUD de todas las
apps, el dashboard con las métricas financieras, las consultas ORM avanzadas, el middleware
de auditoría, Docker Compose y todo lo que estás leyendo ahora mismo.

**Álvaro** se encargó de los datos: los modelos, las relaciones entre ellos, las restricciones,
las migraciones y las funcionalidades que requieren Q objects, F expressions, annotate,
aggregate y la optimización de consultas con select_related y prefetch_related.

