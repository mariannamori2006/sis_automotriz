from django.db import models
from .Cliente import Cliente

class Vehiculo(models.Model):
    id = models.BigAutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='vehiculos')
    placa = models.CharField(max_length=10)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    anio = models.PositiveBigIntegerField()
    color = models.CharField(max_length=30)
    kilometraje = models.PositiveBigIntegerField()

    def __str__(self):
        return f"{self.placa} - {self.marca} {self.modelo}"
