# The Final Djanging :finnadie:

## Día 1 (Maneater) :goberserk:
Después de replantearme mucho mi vida...

He creado el repositorio en GitHub y añadido a Jaime y a Álvaro. También he documentado y creado los modelos, he configurado PostgreSQL con su .env y he creado el requirements.txt y un superusuario. He realizado unas configuraciones básicas de la vista de admin, he configurado algunas cosas en el settings, como las apps, la base de datos y el AUTH_USER_MODEL. He creado el .gitignore (evidentemente) y le he añadido el .env (no queremos que los datos de la base de datos ni la SECRET_KEY se versionen), el .venv (para no tener todas las dependencias del entorno versionándose), .idea y el .git. Para finalizar hoy subire el proyecto a github (no lo habia subido).

Tiempo empleado: 7:30 a 22:10 en el momento en que estoy escribiendo esto.

Observaciones: Mañana será otro día.

P.D.: Jaime y Álvaro hoy no han hecho nada (que yo sepa) porque les dije expresamente que no hicieran nada hasta que no tuviera los modelos listos. Si hay que acarrearle las culpas a alguien, es a mí.

## Día 2 (La leyenda del tiempo) :shipit:
Después de encargarme de asuntos personales externos al desarrollo...

Empecé por realizar unos pequeños cambios en el modelo presupuesto. Simplemente le añadí una señal para asegurarme de que un presupuesto no aceptado o no rechazado, cuando se modifique compruebe su fecha de validez y si esta ha caducado, que marque el presupuesto como rechazado.


Después cree los grupos FREELANCER y CLIENTE con sus permisos en la base de datos y cree signals en usuarios y clientes:

El signals.py de usuarios, en base al tipo de cuenta del perfil asigna a un usuario a un grupo o a otro

Y el de cliente, si el cliente es modificado y se le asigna un usuario, que se agregue automaticamente al grupo CLIENTE


A continuación creé una aplicacion llamada setup para hacer una migracion y en ella crear los grupos FREELANCER y CLIENTE con sus permisos y de esa forma facilitar la vida a los intengrantes del equipo al ellos solo tener que hacer el migrate para tener todos los grupos configurados

Y, para finalizar, creé los mixins personalizados (pone un en el enunciado, yo hice los 2) FreelancerPropietario y ClientePropietarioMixin dentro de setup y documenté los middlewares relacionados con la seguridad, sesiones y autenticación (en el enunciado pone 1 yo los hice todos los relacionados).

Tiempo empleado: 16:00 a 21:15 en el momento en que estoy escribiendo esto.

Observaciones: Mañana quiero hacer más.


## Día 3 (Billie Jean) :finnadie:
Hoy he borrado las migraciones de presupuestos y facturas y las he vuelto a migrar para conseguir un poco más de limpeza. También he modificado el migrate de 0001_initial.py de setup, para que apunte correctamente a las migraciones de presupuestos y facturas.

Hice dos pushes a esto por que, seguramente, desmarcaría sin querer el migrate de facturas


Hice los forms.py de los modelos y modifique algunos de estos para aádirles validaciones que se me pasaron a la hora de crearlos

Tambien empecé con la dockerizacion del proyecto pero, la verdad, es que estaba / estoy muy saturado y no estoy dando pie con vola. Mañana puede que me de el dia libre para despejarme y tener la mente más despejada, aunque a lo mejor es un lujo que no me puedo permitir.

Tiempo empleado: 10:30 a 19:51 en el momento en que estoy escribiendo esto.

Observaciones: quiero entregar este trabajo suspender y seguir con mi vida