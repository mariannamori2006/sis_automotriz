from datetime import date, time
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Cliente, Vehiculo, Mecanico, Cita, Diagnostico, Repuesto, OrdenServicio


class AutomotrizTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='profe', password='ClaveSegura123#')
        self.cli = Cliente.objects.create(
            nombres='Ana', apellidos='Pérez', dni='00000001', telefono='999999999',
            correo='ana@example.com', direccion='Av. Principal 123')
        self.veh = Vehiculo.objects.create(
            cliente=self.cli, placa='ABC-123', marca='Toyota', modelo='Corolla',
            anio=2018, color='Blanco', kilometraje=50000)
        self.mec = Mecanico.objects.create(
            nombres='Luis', apellidos='Ramos', dni='00000002', especialidad='Motor',
            telefono='988888888', correo='luis@example.com')
        self.cita = Cita.objects.create(
            vehiculo=self.veh, mecanico=self.mec, fecha=date(2026, 11, 12),
            hora=time(10, 30), motivo='Mantenimiento')
        self.diag = Diagnostico.objects.create(
            cita=self.cita, descripcion_problema='Ruido en el motor', causa='Correa desgastada',
            solucion_recomendada='Cambiar correa', fecha=date(2026, 11, 12),
            costo_estimado=Decimal('150.00'))
        self.rep = Repuesto.objects.create(
            codigo='REP-001', nombre='Correa de distribución', descripcion='Correa original',
            marca='Gates', precio=Decimal('50.00'), stock=10)
        self.orden = OrdenServicio.objects.create(
            diagnostico=self.diag, repuesto=self.rep, descrpcion_trabajo='Cambio de correa',
            cantidad_repuesto=2, costo_mano_obra=Decimal('80.00'),
            fecha_inicio=date(2026, 11, 13), fecha_entrega=date(2026, 11, 14))

    def test_login_requerido(self):
        r = self.client.get(reverse('listado', args=['vehiculos']))
        self.assertEqual(r.status_code, 302)

    def test_crud_de_siete_tablas(self):
        self.client.force_login(self.usuario)
        secciones = ['clientes', 'vehiculos', 'mecanicos', 'citas', 'diagnosticos', 'repuestos', 'ordenes']
        for seccion in secciones:
            self.assertEqual(self.client.get(reverse('listado', args=[seccion])).status_code, 200)
            self.assertEqual(self.client.get(reverse('nuevo', args=[seccion])).status_code, 200)
        objetos = [('clientes', self.cli), ('vehiculos', self.veh), ('mecanicos', self.mec),
                   ('citas', self.cita), ('diagnosticos', self.diag), ('repuestos', self.rep),
                   ('ordenes', self.orden)]
        for seccion, obj in objetos:
            self.assertEqual(self.client.get(reverse('editar', args=[seccion, obj.pk])).status_code, 200)

    def test_reportes_e_impresiones(self):
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(reverse('reporte')).status_code, 200)
        for seccion, obj in [('citas', self.cita), ('diagnosticos', self.diag), ('ordenes', self.orden)]:
            self.assertEqual(self.client.get(reverse('imprimir', args=[seccion, obj.pk])).status_code, 200)

    def test_eliminar_no_permitido_por_get(self):
        self.client.force_login(self.usuario)
        r = self.client.get(reverse('eliminar', args=['ordenes', self.orden.pk]))
        self.assertEqual(r.status_code, 405)

    def test_no_eliminar_registro_con_dependencias(self):
        self.client.force_login(self.usuario)
        r = self.client.post(reverse('eliminar', args=['clientes', self.cli.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Cliente.objects.filter(pk=self.cli.pk).exists())

    def test_no_duplicar_mecanico_en_misma_fecha_hora(self):
        from django.db import IntegrityError, transaction
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Cita.objects.create(vehiculo=self.veh, mecanico=self.mec,
                                    fecha=date(2026, 11, 12), hora=time(10, 30), motivo='Revisión')

    def test_costo_total_de_orden_se_calcula(self):
        # 80 (mano de obra) + 50 * 2 (repuesto) = 180
        self.assertEqual(self.orden.costo_total, Decimal('180.00'))

    def test_crear_cliente_y_eliminar_repuesto_sin_dependencias(self):
        self.client.force_login(self.usuario)
        r = self.client.post(reverse('nuevo', args=['clientes']), {
            'nombres': 'Pedro', 'apellidos': 'García', 'dni': '12345678',
            'telefono': '900000001', 'correo': 'pedro@example.com', 'direccion': 'Calle 1'
        })
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Cliente.objects.filter(dni='12345678').exists())
        otro = Repuesto.objects.create(codigo='REP-002', nombre='Filtro', descripcion='Filtro de aceite',
                                       marca='Bosch', precio=Decimal('20.00'), stock=5)
        self.assertEqual(self.client.post(reverse('eliminar', args=['repuestos', otro.pk])).status_code, 302)
        self.assertFalse(Repuesto.objects.filter(pk=otro.pk).exists())

    def test_login_recordarme(self):
        r = self.client.post(reverse('login'), {'username': 'profe', 'password': 'ClaveSegura123#', 'recordarme': '1'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.client.session.get_expiry_age() // 86400, 14)

    def test_registro_en_desarrollo(self):
        r = self.client.post(reverse('registro'), {
            'username': 'alumno', 'email': 'alumno@example.com',
            'password1': 'UnaClaveSegura123#', 'password2': 'UnaClaveSegura123#'})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(User.objects.filter(username='alumno').exists())