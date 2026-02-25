import logging
from django.utils import timezone

"""
Middleware personalizado: AuditoriaMiddleware

Problema que resuelve:
    Registrar automáticamente los accesos a rutas sensibles del sistema
    (convertir presupuesto a factura, registrar pago, cambiar estado de factura)
    para que quede trazabilidad de quién hizo qué y cuándo.

Rutas que afecta:
    - /presupuestos/<id>/convertir/   → conversión de presupuesto a factura
    - /facturas/<id>/registrar-pago/  → registro de un pago en una factura
    - /facturas/<id>/estado/          → cambio de estado de una factura

Comportamiento esperado:
    - Si un usuario autenticado accede a /presupuestos/5/convertir/ mediante POST,
      el middleware registra en el log: quién, qué ruta, qué método y a qué hora.
    - Si un usuario no autenticado intenta acceder, se registra como 'anonimo'.
    - Las rutas no sensibles no generan ningún registro, el middleware las ignora.

Ejemplo de log generado:
    [AUDITORIA] 2026-02-25 10:32:11 | usuario: admin | POST /presupuestos/5/convertir/
    [AUDITORIA] 2026-02-25 11:05:44 | usuario: admin | POST /facturas/3/registrar-pago/
"""

# Logger propio para la auditoría, se puede redirigir a fichero en settings si se desea
logger = logging.getLogger('auditoria')

# Rutas sensibles que deben auditarse
RUTAS_SENSIBLES = [
    '/convertir/',
    '/registrar-pago/',
    '/estado/',
]


class AuditoriaMiddleware:
    """
    Middleware de auditoría que registra los accesos a rutas sensibles.

    Se ejecuta en cada petición y comprueba si la ruta actual coincide
    con alguna de las rutas sensibles definidas. Si coincide, registra
    en el log el usuario, la ruta, el método HTTP y la fecha y hora.
    """

    def __init__(self, get_response):
        """
        Se ejecuta una sola vez al arrancar el servidor.
        Recibe get_response, que es el siguiente middleware o la vista final.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Se ejecuta en cada petición HTTP.

        Comprueba si la ruta actual es sensible y, si lo es,
        registra el acceso antes de pasar la petición al siguiente middleware.
        """
        # Comprobamos si la ruta actual contiene alguna de las rutas sensibles
        es_ruta_sensible = any(ruta in request.path for ruta in RUTAS_SENSIBLES)

        if es_ruta_sensible:
            # Obtenemos el nombre del usuario o 'anonimo' si no está autenticado
            usuario = request.user.username if request.user.is_authenticated else 'anonimo'
            ahora = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

            logger.warning(
                f'[AUDITORIA] {ahora} | usuario: {usuario} | {request.method} {request.path}'
            )

        # Pasamos la petición al siguiente middleware o a la vista
        response = self.get_response(request)

        return response