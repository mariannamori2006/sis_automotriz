from django.contrib import admin
from .models import Cita, Cliente, Diagnostico, Mecanico, OrdenServicio, Repuesto, Vehiculo
for modelo in (Cita, Cliente, Diagnostico, Mecanico, OrdenServicio, Repuesto, Vehiculo):
    admin.site.register(modelo)
admin.site.site_header = 'Automotriz - Administración'
