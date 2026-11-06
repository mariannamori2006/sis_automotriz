from django.urls import path
from . import views
urlpatterns = [
 path('', views.inicio,name='inicio'),
 path('reportes/citas/',views.reporte,name='reporte'),
 path('<str:seccion>/',views.listado,name='listado'),
 path('<str:seccion>/nuevo/',views.guardar,name='nuevo'),
 path('<str:seccion>/editar/<int:pk>/',views.guardar,name='editar'),
 path('<str:seccion>/eliminar/<int:pk>/',views.eliminar,name='eliminar'),
 path('<str:seccion>/imprimir/<int:pk>/',views.imprimir,name='imprimir'),
]
