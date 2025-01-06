// Función para alternar entre las pestañas
function showTab(tabName) {
    // Ocultar todas las pestañas
    var tabs = document.querySelectorAll('.content div');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Mostrar la pestaña seleccionada
    var activeTab = document.getElementById(tabName);
    activeTab.classList.add('active');

    // Cambiar el estilo activo para las pestañas
    var tabLinks = document.querySelectorAll('.tab');
    tabLinks.forEach(tabLink => tabLink.classList.remove('active'));
    document.querySelector(`.tab[onclick="showTab('${tabName}')"]`).classList.add('active');
}