-- Crear tabla de carros con la cantidad de gallinas
CREATE TABLE IF NOT EXISTS gallinas_carro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    carro INTEGER NOT NULL UNIQUE,
    cantidad_gallinas INTEGER NOT NULL,
    fecha DATE DEFAULT CURRENT_DATE
);

-- Crear tabla de recolecciones (huevos recolectados y huevos rotos)
CREATE TABLE IF NOT EXISTS recolecciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    carro INTEGER NOT NULL,
    cantidad_huevos INTEGER NOT NULL,
    huevos_rotos INTEGER NOT NULL,
    turno TEXT NOT NULL,
    fecha DATE DEFAULT CURRENT_DATE
);

-- Crear tabla de stock total (huevos recolectados en total)
CREATE TABLE IF NOT EXISTS stock_total (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cantidad_huevos INTEGER NOT NULL,
    fecha_actualizacion DATE DEFAULT CURRENT_DATE
);

-- Crear tabla de armado (maplets y cajas)
CREATE TABLE IF NOT EXISTS armado (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL, -- 'maplet' o 'caja'
    categoria TEXT, -- Solo aplica a maplets (Premium, Grandes, etc.)
    cantidad INTEGER NOT NULL,
    fecha DATE DEFAULT CURRENT_DATE
);


CREATE TABLE IF NOT EXISTS ventas_maplets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendedor TEXT NOT NULL,
    categoria TEXT NOT NULL,  -- Solo aplica para maplets
    cantidad INTEGER NOT NULL,
    fecha DATE DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS ventas_cajas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendedor TEXT NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha DATE DEFAULT CURRENT_DATE
);

-- Crear tabla de maplets armados
CREATE TABLE IF NOT EXISTS maplets_armados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria TEXT NOT NULL, -- 'Premium', 'Grandes', etc.
    cantidad INTEGER NOT NULL,
    fecha DATE DEFAULT CURRENT_DATE
);

-- Crear tabla de cajas armadas
CREATE TABLE IF NOT EXISTS cajas_armadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cantidad INTEGER NOT NULL,
    fecha DATE DEFAULT CURRENT_DATE
);