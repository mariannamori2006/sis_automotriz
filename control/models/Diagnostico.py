from django.db import models
from .Cita import Cita

class Diagnostico(models.Model):
    id = models.BigIntegerField(primary_key=True)
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE, related_name='diagnosticos')
    descripcion_problema = models.TextField()
    causa = models.TextField()
    solucion_recomendada = models.TextField()
    fecha = models.DateField()
    costo_estimado = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Diagnostico {self.id} Cita {self.cita_id}"
    