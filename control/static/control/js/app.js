document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.formulario-eliminar').forEach(function (formulario) {
    formulario.addEventListener('submit', function (evento) {
      if (!window.confirm('¿Eliminar este registro? La operación no se puede deshacer.')) evento.preventDefault();
    });
  });
});
