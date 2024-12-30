// Archivo: static/js/validaciones.js

// Función para extraer parámetros de la URL
function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

// Mostrar alerta si hay un mensaje en los parámetros de la URL
document.addEventListener("DOMContentLoaded", () => {
    const mensaje = getQueryParam("mensaje");
    if (mensaje) {
        alert(mensaje);
    }
});

// Validar stock antes de enviar el formulario
function validarStock(event) {
    const categoriaSelect = document.querySelector('select[name="categoria"]');
    const selectedOption = categoriaSelect.options[categoriaSelect.selectedIndex];
    const stockDisponible = parseInt(selectedOption.getAttribute('data-stock'));

    if (stockDisponible <= 0) {
        event.preventDefault(); // Evita que el formulario se envíe
        alert("No se puede ajustar el stock. Stock actual: 0 unidades.");
        return false;
    }

    return true; // Permitir el envío del formulario si el stock es suficiente
}