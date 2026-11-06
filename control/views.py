from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import IntegrityError
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import (ClienteForm, VehiculoForm, MecanicoForm, CitaForm,
                    DiagnosticoForm, RepuestoForm, OrdenServicioForm, RegistroForm)
from .models import (Cliente, Vehiculo, Mecanico, Cita, Diagnostico, Repuesto, OrdenServicio)

# Un mismo patrón CRUD sencillo para las siete tablas.
SECCIONES = {
 'clientes': {'modelo':Cliente,'formulario':ClienteForm,'titulo':'Clientes','campos':['nombres','apellidos','dni','telefono','correo']},
 'vehiculos': {'modelo':Vehiculo,'formulario':VehiculoForm,'titulo':'Vehículos','campos':['placa','cliente','marca','modelo','anio']},
 'mecanicos': {'modelo':Mecanico,'formulario':MecanicoForm,'titulo':'Mecánicos','campos':['nombres','apellidos','dni','especialidad','estado']},
 'citas': {'modelo':Cita,'formulario':CitaForm,'titulo':'Citas','campos':['vehiculo','mecanico','fecha','hora','estado']},
 'diagnosticos': {'modelo':Diagnostico,'formulario':DiagnosticoForm,'titulo':'Diagnósticos','campos':['cita','descripcion_problema','fecha','costo_estimado']},
 'repuestos': {'modelo':Repuesto,'formulario':RepuestoForm,'titulo':'Repuestos','campos':['codigo','nombre','marca','precio','stock','estado']},
 'ordenes': {'modelo':OrdenServicio,'formulario':OrdenServicioForm,'titulo':'Órdenes de servicio','campos':['diagnostico','repuesto','costo_total','fecha_entrega','estado']},
}

BUSQUEDAS = {
 'clientes':['nombres','apellidos','dni'],
 'vehiculos':['placa','marca','modelo','cliente__apellidos'],
 'mecanicos':['nombres','apellidos','dni','especialidad'],
 'citas':['vehiculo__placa','motivo','mecanico__apellidos'],
 'diagnosticos':['cita__vehiculo__placa','descripcion_problema'],
 'repuestos':['codigo','nombre','marca'],
 'ordenes':['diagnostico__cita__vehiculo__placa','repuesto__nombre'],
}

def ingresar(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    formulario = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and formulario.is_valid():
        login(request, formulario.get_user())
        if not request.POST.get('recordarme'):
            request.session.set_expiry(0)  # Cierra al terminar la sesión del navegador.
        else:
            request.session.set_expiry(60 * 60 * 24 * 14)
        return redirect('inicio')
    return render(request, 'control/login.html', {'formulario': formulario, 'registro_abierto':settings.REGISTRATION_OPEN})

def registro(request):
    if not settings.REGISTRATION_OPEN:
        raise Http404('Registro deshabilitado. Contacta al administrador.')
    if request.user.is_authenticated:
        return redirect('inicio')
    formulario = RegistroForm(request.POST or None)
    if request.method == 'POST' and formulario.is_valid():
        usuario = formulario.save(commit=False)
        usuario.email = formulario.cleaned_data['email']
        usuario.save()
        login(request, usuario)
        request.session.set_expiry(0)
        messages.success(request, 'Cuenta creada correctamente.')
        return redirect('inicio')
    return render(request, 'control/registro.html', {'formulario':formulario})

@login_required
@require_POST
def salir(request):
    logout(request)
    return redirect('login')

@login_required
def inicio(request):
    resumen = [(item['titulo'], item['modelo'].objects.count(), nombre) for nombre,item in SECCIONES.items()]
    proximas = Cita.objects.select_related('vehiculo','mecanico').order_by('fecha','hora')[:8]
    return render(request, 'control/inicio.html', {'resumen':resumen, 'proximas':proximas})

@login_required
def listado(request, seccion):
    info = SECCIONES.get(seccion)
    if info is None: raise Http404('Sección no disponible')
    objetos = info['modelo'].objects.all()
    if seccion=='vehiculos': objetos=objetos.select_related('cliente')
    if seccion=='citas': objetos=objetos.select_related('vehiculo','mecanico')
    if seccion=='diagnosticos': objetos=objetos.select_related('cita__vehiculo')
    if seccion=='ordenes': objetos=objetos.select_related('diagnostico__cita__vehiculo','repuesto')
    q = request.GET.get('q','').strip()[:100]
    if q:
        filtro=Q()
        for campo in BUSQUEDAS[seccion]: filtro |= Q(**{campo+'__icontains':q})
        objetos=objetos.filter(filtro)
    objetos=objetos[:300]
    filas=[[getattr(obj, campo) for campo in info['campos']] for obj in objetos]
    datos=list(zip(objetos,filas))
    return render(request,'control/listado.html',{'info':info,'seccion':seccion,'datos':datos,'q':q})

@login_required
def guardar(request, seccion, pk=None):
    info=SECCIONES.get(seccion)
    if info is None: raise Http404('Sección no disponible')
    objeto=get_object_or_404(info['modelo'],pk=pk) if pk else None
    formulario=info['formulario'](request.POST or None,instance=objeto)
    if request.method=='POST' and formulario.is_valid():
        try:
            formulario.save()
            messages.success(request,'Registro guardado correctamente.')
            return redirect('listado',seccion=seccion)
        except IntegrityError:
            formulario.add_error(None,'No se pudo guardar: dato duplicado o relación inválida.')
    return render(request,'control/formulario.html',{'formulario':formulario,'info':info,'seccion':seccion,'objeto':objeto})

@login_required
@require_POST
def eliminar(request, seccion, pk):
    info=SECCIONES.get(seccion)
    if info is None: raise Http404('Sección no disponible')
    objeto=get_object_or_404(info['modelo'],pk=pk)
    try:
        objeto.delete()
        messages.success(request,'Registro eliminado.')
    except ProtectedError:
        messages.error(request,'No se puede eliminar: tiene registros relacionados. Elimina primero los dependientes.')
    return redirect('listado',seccion=seccion)

@login_required
def imprimir(request, seccion, pk):
    if seccion not in ('citas','diagnosticos','ordenes'):
        raise Http404('Documento no disponible')
    modelo=SECCIONES[seccion]['modelo']
    objeto=get_object_or_404(modelo, pk=pk)
    return render(request,'control/impresion.html',{'objeto':objeto,'seccion':seccion})

@login_required
def reporte(request):
    citas=Cita.objects.select_related('vehiculo__cliente','mecanico').all()
    inicio=request.GET.get('desde','')
    fin=request.GET.get('hasta','')
    estado=request.GET.get('estado','')
    from datetime import date
    try:
        if inicio: citas=citas.filter(fecha__gte=date.fromisoformat(inicio))
        if fin: citas=citas.filter(fecha__lte=date.fromisoformat(fin))
    except ValueError:
        messages.error(request,'Las fechas deben tener formato AAAA-MM-DD.')
        return redirect('reporte')
    if estado in dict(Cita.ESTADOS): citas=citas.filter(estado=estado)
    return render(request,'control/reporte.html',{'citas':citas[:500],'desde':inicio,'hasta':fin,'estado':estado,'estados':Cita.ESTADOS})