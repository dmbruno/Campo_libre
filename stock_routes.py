from flask import Blueprint, render_template, request, jsonify
import sqlite3

# Crear un Blueprint para las rutas de ajustes de stock
ajustes_stock_bp = Blueprint('ajustes_stock', __name__)

# Ruta para mostrar la página de ajustes de stock
@ajustes_stock_bp.route('/ajustes_stock')
def ajustes_stock():
    conn = sqlite3.connect('campo_libre.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(cantidad_huevos) AS total_huevos FROM stock_total")
    stock_huevos_row = cursor.fetchone()
    stock_huevos = stock_huevos_row['total_huevos'] if stock_huevos_row and stock_huevos_row['total_huevos'] is not None else 0

    cursor.execute("""
        WITH categorias AS (
            SELECT 'Premium' AS categoria
            UNION ALL
            SELECT 'Grandes'
            UNION ALL
            SELECT 'Medianos'
            UNION ALL
            SELECT 'Pequeños'
            UNION ALL
            SELECT 'Doble Yema'
        )
        SELECT 
            categorias.categoria,
            IFNULL(SUM(maplets_armados.cantidad), 0) AS total_maplets
        FROM 
            categorias
        LEFT JOIN 
            maplets_armados
        ON 
            categorias.categoria = maplets_armados.categoria
        GROUP BY 
            categorias.categoria;
    """)
    maplets = cursor.fetchall()

    cursor.execute("SELECT SUM(cantidad) AS total_cajas FROM cajas_armadas")
    cajas = cursor.fetchone()

    conn.close()

    return render_template(
        'ajustes_stock.html',
        stock_huevos={'total_huevos': stock_huevos},
        maplets=maplets,
        cajas=cajas
    )

# Ruta para actualizar los datos de stock
@ajustes_stock_bp.route('/actualizar-stock', methods=['POST'])
def actualizar_stock():
    data = request.json
    conn = sqlite3.connect('campo_libre.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Manejo de actualización para huevos
    if 'cantidad_huevos' in data:
        try:
            nueva_cantidad = int(data['cantidad_huevos'])  # Asegurarse de que sea un número entero
            # Insertamos la nueva cantidad como un registro adicional
            cursor.execute("INSERT INTO stock_total (cantidad_huevos) VALUES (?)", (nueva_cantidad,))
        except ValueError:
            return jsonify({'message': 'Error: cantidad_huevos debe ser un número válido'}), 400

    # Manejo de actualización para maplets
    if 'maplets' in data:
        for categoria, cantidad in data['maplets'].items():
            try:
                nueva_cantidad = int(cantidad)

                # Verificar si la categoría ya existe en la tabla
                cursor.execute("SELECT id FROM maplets_armados WHERE categoria = ?", (categoria,))
                row = cursor.fetchone()

                if row:
                    # Si ya existe, actualizamos la cantidad
                    cursor.execute(
                        "UPDATE maplets_armados SET cantidad = cantidad + ? WHERE categoria = ?",
                        (nueva_cantidad, categoria)
                    )
                else:
                    # Si no existe, insertamos un nuevo registro
                    cursor.execute(
                        "INSERT INTO maplets_armados (categoria, cantidad) VALUES (?, ?)",
                        (categoria, nueva_cantidad)
                    )

            except ValueError:
                return jsonify({'message': f'Error: cantidad para {categoria} debe ser un número válido'}), 400

    
    # Manejo de actualización para cajas
    if 'cantidad_cajas' in data:
        try:
            nueva_cantidad = int(data['cantidad_cajas'])
            cursor.execute("UPDATE cajas_armadas SET cantidad = cantidad + ?", (nueva_cantidad,))
        except ValueError:
            return jsonify({'message': 'Error: cantidad_cajas debe ser un número válido'}), 400

    # Guardar cambios y cerrar la conexión
    conn.commit()
    conn.close()

    # Recalcular el total para devolverlo al cliente
    conn = sqlite3.connect('campo_libre.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(cantidad_huevos) AS total_huevos FROM stock_total")
    total_huevos = cursor.fetchone()['total_huevos']
    conn.close()

    return jsonify({'message': 'Stock actualizado con éxito', 'total_huevos': total_huevos})