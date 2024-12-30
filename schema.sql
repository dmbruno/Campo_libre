-- Crear tabla recolecciones
CREATE TABLE recolecciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    carro INTEGER NOT NULL,
    categoria TEXT NOT NULL,
    cantidad INTEGER NOT NULL,
    turno TEXT NOT NULL,
    fecha DATE DEFAULT CURRENT_DATE
);

-- Crear tabla ventas
CREATE TABLE ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendedor TEXT NOT NULL,
    categoria TEXT NOT NULL,
    maplets INTEGER NOT NULL,
    cajas INTEGER NOT NULL,
    fecha DATE DEFAULT CURRENT_DATE
);

-- Crear tabla stock
CREATE TABLE stock (
    categoria TEXT PRIMARY KEY,
    total_huevos INTEGER NOT NULL
);