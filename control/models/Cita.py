from django.db import models
from .Vehiculo import Vehiculo
from .Mecanico import Mecanico

class Cita(models.Model):
    ESTADOS = [("pendiente", "Pendiente"), ("confirmada", "Confirmada"), ("atendida", "Atendida")]

    id = models.BigIntegerField(primary_key=True)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='citas')
    mecanico = models.ForeignKey(Mecanico, on_delete=models.CASCADE, related_name='citas')
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.CharField(max_length=200)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    observaciones = models.TimeField(blank=True)

    def __str__(self):
        return f"Cita {self.id} - {self.vehiculo.placa} ({self.fecha})"