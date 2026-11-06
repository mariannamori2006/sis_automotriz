from django.db import models

class Repuesto(models.Model):
    ESTADO = [("disponible", "Disponible"), ("agotado", "Agotado")]
    id = models.BigAutoField(primary_key=True)
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    marca = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveBigIntegerField()
    estado = models.CharField(max_length=20, choices=ESTADO, default="disponible")

    def __str__(self):
        return f"{self.codigo} - {self.nombre}" 