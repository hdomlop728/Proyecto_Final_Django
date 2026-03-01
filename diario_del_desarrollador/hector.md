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


## Día 4 (Songbird - Kenny G) :saxophone:
Me tome el dia libre para despejarme un poco, no se si habrá valido de algo, pero he de continuar.


## Día 5 (Thriller) :movie_camera:
Hoy he desarrollado la vista de auth, me tiré mucho tiempo ''''''''arreglando'''''''' permisos de los usuarios y con ''''''arreglando'''''''' me refiero a tocar el signals de usuario porque a los usuarios se les estaban asignando los grupos pero no veia los permisos y lo que pasaba es que se les asignaba a nivel de grupo y no de usuario por lo que no se veian en la vista de admin, se veian haciendo consultas en el shell. También modifique UsuarioRegistroForm porque se me olvido poner los campos de perfil y el admin para tener una vista más detallada en admin. Hice los urls (casi todos sin contenidos) y algunos templates y archivos estaticos junto a su configuración.

Tiempo empleado: 7:15 a 12:20 más o menos

Observaciones: Probablemente, no haya más actualizaciones de mi parte por que sino Jaime y Álvaro me matan, con excepción del usuario personalizado que lo quiero terminar. Cuando termine el desarrollo daré mis conclusiones


## Día 6 (Challengers - DBZ: Budokai) :trollface:
He hecho una modificación al modelo facturas, para añadir el campo total_pagado y hacer consultas con F expressions (tambien modifique levemente su forms.py ya que tenia el campo total_pagado). 

Tambien he modificado levemente el foms.py de cliente porque tenia un fallito. Basicamente, se me habia pasado añadir el campo freelancer y daba un error al crear un cliente desde la vista.

Después he modificado un poquito la estructura de los admin.py para facilitar (un poco) a quien se encargue de ellos (todavía por definir).

Hoy no he sido constante el desarrollo, debido a motivos personales, entonces he estado desarrollando y probando cuando he podido en el día




Tiempo empleado: 4 horas (diría)

Observaciones: He encontrado un pequeño fallo a la hora de usar el migrate del setup que se encarga de crear los grupos con sus permisos, se crean los grupos, se crean los permisos pero por lo menos en la vista de admin no se ven aplicados a los grupos. Mañana me pondré a enredar. Y al final si van a seguir habiendo actualizaciones de mi parte. 


ACTUALIZACIÓN: Supuestamente el migrate de setup para hacer los grupos con sus permisos, va como un tiro, solo que me faltaba el una funcion para eliminar los grupos si existian, pero los permisos a los grupos se asignan de forma correcta. 

Lo de los permisos que no se aplican a los grupos, es que me lo enseño Jaime, pero yo lo he probado y funciona, tal vez ha sido algún fallo en las migraciones, igualmente seguiré atento, con respecto a este tema. Y además al hacer esto me di cuenta que al hacer los cambios al modelo facturas no los migre, así que lo corregí


P.D: Jaime era el encargado de las consultas ORM, pero yo me puse a mirarlas antes que el y vi la de F expressions y le dije que como tocaba el modelo, me encargaba yo. Si Jaime ha hecho menos ahí, es culpa mia


## Día 7 (Proto Man Castle - Mega Man 5) :finnadie:
Corregí un cambio que hice en el forms.py de clientes porque soy idiota y no se leer un comentario que dice, el campo freelancer no lo pongo porque el freelancer se asigna de forma automatica por el request.user. Simplemente soy tonto por decir: 
- Oh, Jaime a hecho algo
- Lo que ha hecho no le funciona
- Será cosas de los modelos y formularios
- No lo erá. Era cosa de lo que habia hecho él y ahora tengo que corregir lo suyo y lo mio.

Soy muy tonto

También corregí lo que le fallaba en la vista a Jaime

Después me encargue de revisar cosas que hizo Álvaro (a ojo). Y, externamente a este proyecto, ayudé un poco al grupo 8 para implementar postgre

Tiempo empleado: 4 horas (diría)

Observaciones: Quiero terminar YA.


## Día 8 (Nightrain) :goberserk:
He justificado porque he escogido usar AbstractUser para la creación del usuario personalizado. 

Probé un poco las vistas (van como la mierda) corregí levemente las algunas cosas de ellas. Y tabién corregí y mejoré algunas cosas del modelo y el form factura.

Tiempo empleado: 4 horas (diría)

Observaciones: Quiero escribir el reporte final del proyecto.

## Día 9 (Dreamer - SOR 2) :japanese_goblin: 
Corregí un error que Álvaro creo en el base.html y mejoré las vistas de admin (se lo encargué a ellos pero, vamos a entregar el proyecto y todavía estaré esperando a que las hagan)

Tiempo empleado: 3-4 horas diría

Observaciones: Me da tanta vergüenza, tener que enseñar este proyecto

## Día 10 (Maniac) :feelsgood:
Hice unas pruebas en clientes y me dí cuenta de que habia unos pequeños fallos en el clean, los corregí.

Me quiero poner a intentar hacer los puntos opciones entre hoy y mañana (también se lo encargue a ellos pero, lo mismo como espere, no se entrega con eso), de momento llevo el 1º el transformar una factura a PDF utilize weasyprint. Al tener que instalarlo como una dependecia tuve actualizar el requirements.txt con el comando que especifico en requerimientos.txt.

Si no puedo hacerlos todos, pues ya no le puedo hacer más.

Al final hoy por motivos personales, no pude continuar con los otros puntos opcionales. Y solo haré el último punto (junto al primero que ya esta hecho) porque el para el segundo me hace falta la vista de dashboard y como no funciona, pues me jodo (y no la pienso arreglar, que le apañe un potaje)

Tiempo empleado: 5 horas (diría)

Observaciones: Espero mañana contar con el tiempo para poder hacer el último punto y subirlo (yo creo que si)


## Día 11 (Sadness - Sonic Adventure) :finnadie:
Realizé la exportacion de las facturas a formato csv filtrandolas por su estado, termine de modificar el README.md y este archivo y en cuanto lo pusheé lo entregaré

Tiempo empleado: 5:00 - 9:00, en el momento de escribir esto

Observaciones: Me hubiera gustado hacer el segundo punto opcional pero como el dashboard no funciona es como dar escopetazos a ver si funciona

## Observaciones
Este ha sido un proyecto el cual me ha agobiado mucho, muchos dias no he dormido bien (he tenido hasta pesadillas) porque el equipo no hacia nada y cuando lo hacian no estaba bien y el proyecto no llegaba al nivel. El equipo no ha hecho casi nada ha derechas y por decir que lo han hecho ellos, porque el autor de sus aportaciones es chatgpt además de empezar el martes (ha diferencia de lo que diga Jaime (o chatgpt) en su diario). Yo como teamlead creo que lo podría haber hecho algo mejor, tal vez exigirles algo más al equipo, pero es que tampoco soy sus padres para exigirles nada. Y en otros puntos creo que lo podría haber hecho algo mejor.

Rivas, si leé esto, le pido perdón por el bajo nivel del proyecto, entendería perfectamente que tuviese que ir a Junio, porque este trabajo no da la talla ni por asomo. Quiero decir que realmente haciendo mi parte me lo pasé '''bien''' (notense las comillas), he sacado muchas cosas, como:

- La creación de un usuario personalizado (en el examén no lo tenia todo lo preparado que querría)
- La creación de mixins (que aunque nos lo explico en clase, aquí es donde realmente le he dado un uso)
- El saber usar postgre
- El uso de migrates para la creación de grupos de forma automatica al hacer un migrate
- Un mejor uso de los signals (los entendia, pero creo que ahora voy mucho más preparado)
- Y varias cosas más, sinceramente, me ha servido de mucho. Por lo menos, eso que me llevo.

## Música
Aquí van algunos temas que se han quedado fuera de ponerlos en los dias:

- Dark Red
- Lost Courage - DBZ Budokai Tenkaichi 2
- Cheri Cheri Lady
- Silence - F-Zero
- Silence - F-Zero X
- Zoness - Lylatwars / Star Fox 64
- Wolverine Theme - Marvel Super Heroes Vs Street Fighter
- Encounter - Metal Gear Solid
- Sand Hill - Sonic Adventure
- The Man Who Sold The World
- Invisible
- Kremlantis - Donkey Kong Land
- Eagle Theme - Fighting Street (Street Fighter)
- Character Select - Super Street Fighter IV
- Opening Stage - Rockman X3 (Sega Saturn)
- Ryu's Ending - Street Fighter 2
- Staff Credits - Luigi's Mansion
- Chamber of Reflection
- Lost Impact - Shadow The Hedgehog
- Yell Dead Cell - Metal Gear Solid 2
- Departure - Mega Man Zero 2
- Neo Land - Kururin Paradise
- Conditioned Reflex - Sega Rally Championship
- Gathers Under Night... - UNDER NIGHT IN-BIRTH EXE:LATE
- Blood Drain -Again- - UNDER NIGHT IN-BIRTH EXE:LATE
- Tears - Metal Gear 2: Solid Snake
- Strange World - Mega Man 9
- Gen Theme - Street Fighter Alpha 2
- Credit Roll - Street Fighter Alpha 2
- Konami Logo - Metal Gear Solid
- Zone Clear - Sonic CD
- Boss!! - Sonic CD
- Metallic Madness (Bad Future) - Sonic CD
- Cosmic Eternity - Sonic CD
- Credits - Mega Man X
- Game Over - Altered Beast (Mega Drive)
- Smooth Criminal - Original / Michael Jackson's Moonwalker
- Beat It - Original / Michael Jackson's Moonwalker
- Billie Jean - Michael Jackson's Moonwalker
- Mega Water S - Mega Man: The Wily Wars
- Wily Tower Stage 4 - Mega Man: The Wily Wars
- Stage Select - Mega Man 8
- Dr. Wily Stage 2 - Mega Man 8
- Outride a Crisis - Super Hang-On (Megadrive)
- Art Of Fighting Team Theme - KOF '95
- God Smashing Power - DBZ: Dokkan Battle
- Mad Hat - Wario: Master of Disguise
- Game Over - Super Mario World
- Gloomy Manor - Luigi's Mansion 2
- Wild Soul - DBZ Budokai 2
- Y otros temas junto a todo el ost de los videojuegos de Mega Man