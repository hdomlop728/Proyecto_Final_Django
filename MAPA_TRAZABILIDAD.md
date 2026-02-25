# Mapa de trazabilidad y checklist

A continuación se relacionan los requisitos con los módulos, vistas y evidencias implementadas.

| Requisito | App/Módulo | Vista/Pantalla | Evidencia breve |
|-----------|------------|----------------|-----------------|
| F: CRUD proyectos | apps.proyectos | ProyectoListView, Create, Detail, Update | Listado, formulario y detalle funcionan<br>Filtro de estado con sesión |
| F: CRUD facturas | apps.facturas | FacturaListView, Detail, RegisterPayment | Listado con filtros, detalle muestra pagos<br>Formulario de pago registra correctamente |
| H: Mixins integrados | apps.setup.mixins | Utilizados en todas las CBV sensibles | `LoginRequiredMixin`, `PermissionRequiredMixin` en vistas<br>Mixins propios aplicados a Detail/Update |
| H: Mixin personalizado | apps.setup.mixins | FreelancerPropietarioMixin, ClientePropietarioMixin | Restringen acceso según propietario (freelancer/cliente) |
| K: Cookie preferencia | apps.usuarios.views | set_theme | Enlace en la barra de navegación permite cambiar tema<br>cookie `theme` guardada y usada en `base.html` |
| K: Sesión filtros | apps.proyectos.views, apps.facturas.views | ProyectoListView, FacturaListView | Filtro de estado persiste entre visitas mediante sesión |

Checklist de verificación (seguro para el equipo):

- [x] Cookie de preferencia de interfaz implementada y visible
- [x] Uso de sesión en un flujo real (filtros persistentes)
- [x] Usuario personalizado operativo (ya existente)
- [x] Grupos y permisos aplicados (freelancer vs cliente)
- [x] Hay FBV y CBV en el proyecto (vistas CRUD CBV, acciones puntuales FBV)
- [x] Mixins integrados aplicados
- [x] Middleware integrado configurado (revisar diarios/middleware.md)
- [x] Formulario con validación avanzada (persiste en modelos)
- [x] Relaciones FK/O2O/M2M implementadas con related_name/query_name
- [x] Decisiones on_delete justificadas (comentarios en modelos)
- [x] Funcionalidad con Q objects, F expressions, annotate y aggregate (modelo y vistas)
- [x] Optimización con select_related/prefetch_related aplicada

El archivo `MAPA_TRAZABILIDAD.md` actúa como evidencia para el punto O del enunciado.
