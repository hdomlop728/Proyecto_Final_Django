from django.db import migrations

"""
Migracion creada con el proposito de crear los grupos FREELANCER y CLIENTE de forma automatica al hacer simplemente migrate.
De esa manera facilitando el flujo de trabajo entre los colaboradores 

NOTA IMPORTANTE: HAY QUE TESTEARLO
"""


def crear_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    freelancer, _ = Group.objects.get_or_create(name='FREELANCER')
    cliente, _ = Group.objects.get_or_create(name='CLIENTE')

    permisos_freelancer = Permission.objects.filter(codename__in=[
        'add_cliente', 'change_cliente', 'delete_cliente', 'view_cliente',
        'add_proyecto', 'change_proyecto', 'delete_proyecto', 'view_proyecto',
        'add_presupuesto', 'change_presupuesto', 'delete_presupuesto', 'view_presupuesto',
        'puede_convertir_presupuesto',
        'add_factura', 'change_factura', 'delete_factura', 'view_factura',
        'puede_registrar_pago', 'puede_anular_factura',
    ])
    freelancer.permissions.set(permisos_freelancer)

    permisos_cliente = Permission.objects.filter(codename__in=[
        'view_proyecto', 'view_presupuesto', 'view_factura',
    ])
    cliente.permissions.set(permisos_cliente)


def eliminar_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['FREELANCER', 'CLIENTE']).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0001_initial'),
        ('clientes', '0001_initial'),
        ('proyectos', '0001_initial'),
        ('presupuestos', '0001_initial'),
        ('facturas', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_grupos, eliminar_grupos),
    ]