// Manejar el botón de editar
document.querySelectorAll('.editar-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        // Llenar el formulario con los datos seleccionados
        document.getElementById('recoleccion-id').value = this.dataset.id;
        document.getElementById('carro').value = this.dataset.carro;
        document.getElementById('cantidad_huevos').value = this.dataset.cantidad;
        document.getElementById('huevos_rotos').value = this.dataset.rotos;
        document.getElementById('turno').value = this.dataset.turno;
        document.getElementById('fecha').value = this.dataset.fecha;

        // Cambiar el texto del botón para indicar "Editar"
        document.getElementById('guardar-btn').textContent = 'Editar';
    });
});