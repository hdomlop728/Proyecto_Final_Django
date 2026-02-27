# The Final Djanging — Jaime

## Antes de empezar
El finde previo estuve fuera de Jerez así que no toqué nada hasta el lunes.
Héctor ya tenía los modelos, formularios y toda la base montada, así que me puse a trabajar sobre lo que había.

## Lunes
Empecé con las vistas de clientes y presupuestos. CBV para el CRUD, FBV para las acciones puntuales como convertir presupuesto a factura. También hice las URLs de ambas apps.

Me di cuenta tarde de que había hecho un CRU en vez de un CRUD, es decir, me había olvidado el Delete. Tuve que volver atrás y añadir el DeleteView con su template de confirmación en clientes y presupuestos. Un poco torpe por mi parte.

Tiempo empleado: 16:00 a 20:00

## Martes
Me puse con el dashboard. Quería que tuviera métricas reales así que usé aggregate para los totales, annotate para el ranking de clientes, Q objects para los filtros combinados y F expressions para calcular el pendiente directamente en la base de datos. Los filtros de año y cliente los guardé en sesión para que persistan entre visitas.

Tiempo empleado: 16:00 a 20:00

## Miércoles
Hice las vistas de proyectos y facturas, que estaban vacías. En proyectos aproveché para meter annotate con el número de presupuestos y facturas por proyecto, y prefetch_related en el detalle para evitar el problema N+1. En facturas metí la FBV de registrar pago y la de anular factura.

También hice el middleware de auditoría. Va en apps/setup/middleware.py y registra en consola quién accede a las rutas sensibles. Lo tuve que poner al final del MIDDLEWARE en settings.py porque si no request.user no existe todavía y registra todo como anónimo.

Tiempo empleado: 16:00 a 20:00

## Jueves
Me tocó Docker. Pensé que iba a ser lo más complicado pero fue lo que más rápido salió. Creé el Dockerfile, el docker-compose.yml con los servicios web y db, el volumen para que los datos de PostgreSQL persistan y el .dockerignore. También tuve que tocar el settings.py para añadir localhost y 0.0.0.0 al ALLOWED_HOSTS y que Django aceptara peticiones desde el contenedor.

Tiempo empleado: 16:00 a 20:00

## Viernes
Me encargué de la documentación. El README con todo lo necesario para levantar el proyecto tanto en local como con Docker, las decisiones técnicas explicadas y el workflow del equipo. También el diario (esto que estás leyendo).

Tiempo empleado: 16:00 a 20:00

Observaciones: Contento con cómo quedó el Docker, fue lo que menos guerra me dio. Lo del CRUD me lo apunto para no volver a cometer el mismo error.