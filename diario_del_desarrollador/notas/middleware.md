# Documentación middleware

## django.middleware.security.SecurityMiddleware
- Seguridad general, protege contra ataques XSS, clickjacking, etc.
- Debe ir primero para ejecutarse antes que cualquier otro middleware.

## django.contrib.sessions.middleware.SessionMiddleware
- Gestiona las sesiones de usuario, necesario para que el login funcione.

## django.middleware.csrf.CsrfViewMiddleware
- Protege contra ataques CSRF, genera y valida el token en los formularios.

## django.contrib.auth.middleware.AuthenticationMiddleware
- Asocia el usuario autenticado a cada petición, hace que `request.user` funcione.

## django.middleware.clickjacking.XFrameOptionsMiddleware
- Protege contra clickjacking impidiendo que la web se cargue en un iframe.