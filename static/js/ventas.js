document.addEventListener("DOMContentLoaded", function() {
    const mapletsTab = document.getElementById("maplets-tab");
    const cajasTab = document.getElementById("cajas-tab");
    const mapletsForm = document.getElementById("maplets-form");
    const cajasForm = document.getElementById("cajas-form");

    // Mostrar el formulario de Venta de Maplets
    mapletsTab.addEventListener("click", function() {
        mapletsForm.style.display = "block";
        cajasForm.style.display = "none";
        mapletsTab.classList.add("active");
        cajasTab.classList.remove("active");
    });

    // Mostrar el formulario de Venta de Cajas
    cajasTab.addEventListener("click", function() {
        cajasForm.style.display = "block";
        mapletsForm.style.display = "none";
        cajasTab.classList.add("active");
        mapletsTab.classList.remove("active");
    });
});