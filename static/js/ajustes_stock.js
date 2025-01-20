function actualizarHuevos() {
    const nuevaCantidad = parseInt(document.getElementById('cantidad-huevos').value, 10) || 0;
    fetch('/actualizar-stock', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cantidad_huevos: nuevaCantidad })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        // Actualizamos el total en la página
        document.getElementById('stock-huevos').innerText = data.total_huevos;
    })
    .catch(error => console.error('Error:', error));
}

function actualizarMapletDesdeBoton(button) {
    // Obtener la categoría desde el atributo data-categoria
    const categoria = button.getAttribute('data-categoria');
    const nuevaCantidad = parseInt(document.getElementById(`maplet-${categoria}`).value, 10) || 0;

    fetch('/actualizar-stock', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ maplets: { [categoria]: nuevaCantidad } })
    })
    .then(response => response.json())
    .then(data => alert(data.message))
    .catch(error => console.error('Error:', error));
}

function actualizarCajas() {
    const nuevaCantidad = parseInt(document.getElementById('cantidad-cajas').value, 10) || 0;
    fetch('/actualizar-stock', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cantidad_cajas: nuevaCantidad })
    })
    .then(response => response.json())
    .then(data => alert(data.message))
    .catch(error => console.error('Error:', error));
}


function resetDatabase() {
    if (confirm('¿Estás seguro de que deseas restablecer todos los datos? Esta acción no se puede deshacer.')) {
        fetch('/reset-database', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => alert(data.message))
        .catch(error => console.error('Error:', error));
    }
}