from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.conf import settings
from .models import Cliente, Vehiculo, Mecanico, Cita, Diagnostico, Repuesto, OrdenServicio


class FormularioBase(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            if isinstance(campo.widget, forms.DateInput): campo.widget.input_type = 'date'
            if isinstance(campo.widget, forms.TimeInput): campo.widget.input_type = 'time'
            campo.widget.attrs.setdefault('class', 'campo')


class ClienteForm(FormularioBase):
    class Meta:
        model = Cliente
        fields = ['nombres', 'apellidos', 'dni', 'telefono', 'correo', 'direccion']


class VehiculoForm(FormularioBase):
    class Meta:
        model = Vehiculo
        fields = ['cliente', 'placa', 'marca', 'modelo', 'anio', 'color', 'kilometraje']


class MecanicoForm(FormularioBase):
    class Meta:
        model = Mecanico
        fields = ['nombres', 'apellidos', 'dni', 'especialidad', 'telefono', 'correo', 'estado']


class CitaForm(FormularioBase):
    class Meta:
        model = Cita
        fields = ['vehiculo', 'mecanico', 'fecha', 'hora', 'motivo', 'estado', 'observaciones']
        widgets = {
            'fecha': forms.DateInput(format='%Y-%m-%d'),
            'hora': forms.TimeInput(format='%H:%M'),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }


class DiagnosticoForm(FormularioBase):
    class Meta:
        model = Diagnostico
        fields = ['cita', 'descripcion_problema', 'causa', 'solucion_recomendada', 'fecha', 'costo_estimado']
        widgets = {
            'descripcion_problema': forms.Textarea(attrs={'rows': 3}),
            'causa': forms.Textarea(attrs={'rows': 3}),
            'solucion_recomendada': forms.Textarea(attrs={'rows': 3}),
            'fecha': forms.DateInput(format='%Y-%m-%d'),
        }


class RepuestoForm(FormularioBase):
    class Meta:
        model = Repuesto
        fields = ['codigo', 'nombre', 'descripcion', 'marca', 'precio', 'stock', 'estado']
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 3})}


class OrdenServicioForm(FormularioBase):
    # costo_total no va en el formulario: se calcula en OrdenServicio.save()
    class Meta:
        model = OrdenServicio
        fields = ['diagnostico', 'repuesto', 'descrpcion_trabajo', 'cantidad_repuesto',
                  'costo_mano_obra', 'fecha_inicio', 'fecha_entrega', 'estado']
        widgets = {
            'descrpcion_trabajo': forms.Textarea(attrs={'rows': 3}),
            'fecha_inicio': forms.DateInput(format='%Y-%m-%d'),
            'fecha_entrega': forms.DateInput(format='%Y-%m-%d'),
        }


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Correo electrónico')
    codigo = forms.CharField(label='Código de invitación (solo en producción)', required=False, widget=forms.PasswordInput, help_text='En desarrollo se puede dejar vacío; en producción es obligatorio.')
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email
    def clean_codigo(self):
        from django.utils.crypto import constant_time_compare
        codigo = self.cleaned_data.get('codigo', '')
        if not settings.DEBUG and not constant_time_compare(codigo, settings.REGISTRATION_CODE):
            raise forms.ValidationError('Código de invitación no válido.')
        return codigo