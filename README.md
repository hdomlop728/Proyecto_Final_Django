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
- **Weasyprint** para imprimir las facturas en formato PDF

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
Crea un archivo llamado `.env` con los siguientes valores que puede encontrar en notas dentro del diario del desarrollador

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
Los datos del superusuario por defecto son los que vienen en superuser dentro de notas

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
(Mentira, el DB_HOST tiene que ser igual a db)

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
evita crear un séptimo modelo (No se puede crear, el proyecto solo pueden haber 6) y permite registrar varios pagos por factura. Para poder
hacer consultas ORM sobre el total cobrado, añadimos el campo `total_pagado` que se
actualiza automáticamente con F expressions cada vez que se registra un pago. (Y porque le dedique demasiado tiempo a Clientes como para borrarlo)

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
separadas, nos coordinamos hablando para no pisar el trabajo de los demás (mentira, Jaime se cargo trabajo de Álvaro en el commit [Views y urls de apps/facturas y apps/proyectos](https://github.com/hdomlop728/Proyecto_Final_Django/commit/09607cc4f5ae2b19ea7d92d8cac1984d0b77d38f) y haciendo pull
antes de cada push. Cuando hubo algún conflicto se resolvió en el momento entre los
implicados.

El reparto quedó así:

---
**Héctor**: Se encargó de todo lo relacionado con los modelos, formularios y la lógica de ellos, configuración de la base de datos y dependencias del entorno virtual. Grupos y usuarios, documentó los middleware que venían en Django relacionados con seguridad/sesiones/autenticación (no era lo que se tenía que hacer pero como no sabía lo que había que hacer se puso a hacer eso), creó los mixins personalizados y los dejó listos para que solo se tuviesen que importar y usar en las vistas. Empezó la dockerización pero, aunque no la terminó porque Jaime se encargaría de eso. Utilizó consultas ORM con F expressions para el modelo Facturas. Se encargó de las vistas de auth (registro y login) y de la de pasar facturas a PDF.

Se encargó del testeo y corrección de las partes que se había encargado y un poco de las de los otros (pero, no todas porque ya estaba harto de estar detrás de ellos, probando y corrigiendo las cosas que ellos deberían probar).

---
**Jaime** se encargó de la documentación: las vistas CRUD de las apps de clientes y presupuestos, el dashboard con las métricas financieras, las consultas ORM avanzadas (no todas), el middleware de auditoría, Docker Compose (habría que ver cómo funciona) y todo lo que estás leyendo ahora mismo. (Para su desgracia)

---
**Álvaro** se encargó de las vistas de proyectos y facturas, cookies, implementación de mixins y el mapa de trazabilidad.

---
(Rivas tal vez le recomiendo leer lo que había escrito aquí antes para darse cuenta de quién lo ha escrito realmente y quién no lo ha siquiera leído, compáralo con los commits, mi reporte diario (el de Héctor) y mi futuro escrito referente a este proyecto (espero que tenga ganas de leer) y perdón por el bajo nivel del proyecto, eso es lo que más me molesta, lo siento de verdad)