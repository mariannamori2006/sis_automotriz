from django.db import models

class Mecanico(models.Model):
    ESTADOS = [("Activo", "Activo"), ("Inactivo", "Inactivo")]

    id = models.BigAutoField(primary_key=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    dni = models.CharField(max_length=8, unique=True)
    especialidad = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default="Activo")

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"