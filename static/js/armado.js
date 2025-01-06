// Función para alternar entre los formularios
function switchTab(tab) {
    const mapletForm = document.querySelector('.maplet-form');
    const cajaForm = document.querySelector('.caja-form');
    const tabButtons = document.querySelectorAll('.tab-button');
    const tipoInput = document.getElementById('tipo');

    if (tab === 'maplet') {
        mapletForm.style.display = 'block';
        cajaForm.style.display = 'none';
        tabButtons[0].classList.add('active');
        tabButtons[1].classList.remove('active');
        tipoInput.value = 'maplet'; // Actualizar el valor de tipo
    } else {
        mapletForm.style.display = 'none';
        cajaForm.style.display = 'block';
        tabButtons[0].classList.remove('active');
        tabButtons[1].classList.add('active');
        tipoInput.value = 'caja'; // Actualizar el valor de tipo
    }
}

// Inicializar con el formulario de maplet visible
switchTab('maplet');