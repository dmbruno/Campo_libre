from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import sqlite3
import pandas as pd
from io import BytesIO
import pandas as pd
from stock_routes import ajustes_stock_bp


app = Flask(__name__)


app.register_blueprint(ajustes_stock_bp)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/carros', methods=['GET', 'POST'])
def carros():
    conn = sqlite3.connect('campo_libre.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == 'POST':
        carro = int(request.form['carro'])
        cantidad_gallinas = int(request.form['cantidad_gallinas'])
        fecha = request.form['fecha']  # Obtener la fecha desde el formulario

        # Insertar o actualizar datos del carro con la fecha de modificación
        cursor.execute("""
            INSERT INTO gallinas_carro (carro, cantidad_gallinas, fecha)
            VALUES (?, ?, ?)
            ON CONFLICT(carro)
            DO UPDATE SET cantidad_gallinas=excluded.cantidad_gallinas, fecha=excluded.fecha
        """, (carro, cantidad_gallinas, fecha))

        conn.commit()
        conn.close()
        return redirect(url_for('carros'))

    # Obtener todos los carros
    cursor.execute("SELECT * FROM gallinas_carro")
    carros = cursor.fetchall()
    conn.close()

    return render_template('carros.html', carros=carros)


# Ruta para recolectar huevos
@app.route('/recolectar', methods=['GET', 'POST'])
def recolectar():
    conn = sqlite3.connect('campo_libre.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == 'POST':
        carro = int(request.form['carro'])  # Convertir carro a entero
        cantidad_huevos = int(request.form['cantidad_huevos'])
        huevos_rotos = int(request.form['huevos_rotos'])
        turno = request.form['turno']
        fecha = request.form['fecha']

        # Registrar la recolección
        cursor.execute(
            "INSERT INTO recolecciones (carro, cantidad_huevos, huevos_rotos, turno, fecha) VALUES (?, ?, ?, ?, ?)",
            (carro, cantidad_huevos, huevos_rotos, turno, fecha)
        )

        # Verificar si existe el registro en stock_total
        cursor.execute("SELECT cantidad_huevos FROM stock_total WHERE id = 1")
        stock_actual = cursor.fetchone()

        if stock_actual:
            # Si existe, actualizar el stock total de huevos
            nuevo_stock = stock_actual['cantidad_huevos'] + cantidad_huevos
            cursor.execute("UPDATE stock_total SET cantidad_huevos = ? WHERE id = 1", (nuevo_stock,))
        else:
            # Si no existe, insertar el primer registro en stock_total
            cursor.execute("INSERT INTO stock_total (cantidad_huevos) VALUES (?)", (cantidad_huevos,))

        conn.commit()

    # Obtener historial de recolecciones
    cursor.execute("SELECT * FROM recolecciones ORDER BY fecha DESC")
    recolecciones = cursor.fetchall()

    conn.close()
    return render_template('recolectar.html', recolecciones=recolecciones)


@app.route('/armado', methods=['GET', 'POST'])
def armado():
    conn = sqlite3.connect('campo_libre.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == 'POST':
        tipo = request.form['tipo']  # 'maplet' o 'caja'
        cantidad = int(request.form['cantidad_maplets'] if tipo == 'maplet' else request.form['cantidad_cajas'])
        fecha = request.form['fecha_maplet'] if tipo == 'maplet' else request.form['fecha_caja']

        # Calcular el stock total consolidado
        cursor.execute("SELECT SUM(cantidad_huevos) AS stock_total FROM stock_total")
        stock_actual = cursor.fetchone()
        stock_huevos = stock_actual['stock_total'] if stock_actual and stock_actual['stock_total'] is not None else 0

        if tipo == 'maplet':
            categoria = request.form['categoria_maplet']
            huevos_necesarios = 30 * cantidad

            if stock_huevos < huevos_necesarios:
                conn.close()
                return f"Error: No hay suficiente stock de huevos para armar los maplets. Huevos disponibles: {stock_huevos}, Huevos necesarios: {huevos_necesarios}."

            # Insertar un registro en stock_total para registrar la reducción
            cursor.execute("INSERT INTO stock_total (cantidad_huevos, fecha_actualizacion) VALUES (?, DATE('now'))", (-huevos_necesarios,))

            # Actualizar o insertar el stock de maplets armados por categoría
            cursor.execute("SELECT cantidad FROM maplets_armados WHERE categoria = ?", (categoria,))
            stock_maplets = cursor.fetchone()

            if stock_maplets:
                nuevo_stock_maplets = stock_maplets['cantidad'] + cantidad
                cursor.execute("UPDATE maplets_armados SET cantidad = ? WHERE categoria = ?", (nuevo_stock_maplets, categoria))
            else:
                cursor.execute("INSERT INTO maplets_armados (categoria, cantidad, fecha) VALUES (?, ?, ?)", (categoria, cantidad, fecha))

        elif tipo == 'caja':
            huevos_necesarios = 6 * cantidad

            if stock_huevos < huevos_necesarios:
                conn.close()
                return f"Error: No hay suficiente stock de huevos para armar las cajas. Huevos disponibles: {stock_huevos}, Huevos necesarios: {huevos_necesarios}."

            # Insertar un registro en stock_total para registrar la reducción
            cursor.execute("INSERT INTO stock_total (cantidad_huevos, fecha_actualizacion) VALUES (?, DATE('now'))", (-huevos_necesarios,))

            # Verificar si ya existe un registro para la fecha actual
            cursor.execute("SELECT id, cantidad FROM cajas_armadas WHERE fecha = ?", (fecha,))
            stock_cajas = cursor.fetchone()

            if stock_cajas:
                nuevo_stock_cajas = stock_cajas['cantidad'] + cantidad
                cursor.execute("UPDATE cajas_armadas SET cantidad = ? WHERE id = ?", (nuevo_stock_cajas, stock_cajas['id']))
            else:
                cursor.execute("INSERT INTO cajas_armadas (cantidad, fecha) VALUES (?, ?)", (cantidad, fecha))

        conn.commit()

    # Mostrar el stock actualizado
    cursor.execute("SELECT categoria, cantidad FROM maplets_armados")
    maplets_armados = cursor.fetchall()

    cursor.execute("SELECT SUM(cantidad) AS total_cajas FROM cajas_armadas")
    total_cajas_disponibles = cursor.fetchone()
    total_cajas_disponibles = total_cajas_disponibles['total_cajas'] if total_cajas_disponibles else 0

    # Calcular el stock total consolidado
    cursor.execute("SELECT SUM(cantidad_huevos) AS stock_total FROM stock_total")
    stock_total_huevos_row = cursor.fetchone()
    stock_total_huevos = stock_total_huevos_row['stock_total'] if stock_total_huevos_row else 0

    conn.close()

    return render_template(
        'armado.html',
        maplets_armados=maplets_armados,
        stock_total=stock_total_huevos,
        total_cajas_disponibles=total_cajas_disponibles
    )
    
# Ruta para registrar ventas
@app.route('/venta_maplets', methods=['GET', 'POST'])
def venta_maplets():
    conn = sqlite3.connect('campo_libre.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == 'POST':
        vendedor = request.form['vendedor']
        fecha = request.form['fecha']
        categoria_maplet = request.form['categoria_maplet']
        cantidad_maplets = int(request.form['cantidad_maplets'])

        # Verificar existencia de stock para maplets (suma de todo el stock)
        cursor.execute("SELECT SUM(cantidad) AS total_stock FROM maplets_armados WHERE categoria = ?", (categoria_maplet,))
        maplet_stock = cursor.fetchone()

        if not maplet_stock or maplet_stock['total_stock'] < cantidad_maplets:
            conn.close()
            return "Error: No hay suficiente stock de maplets para vender."

        # Registrar venta de maplets en la tabla de ventas de maplets
        cursor.execute("INSERT INTO ventas_maplets (vendedor, categoria, cantidad, fecha) VALUES (?, ?, ?, ?)",
                       (vendedor, categoria_maplet, cantidad_maplets, fecha))

        # Restar de stock de maplets
        # Obtener todos los registros de la categoría de maplets
        cursor.execute("SELECT id, cantidad FROM maplets_armados WHERE categoria = ?", (categoria_maplet,))
        registros_maplet = cursor.fetchall()

        cantidad_restante = cantidad_maplets
        for registro in registros_maplet:
            if cantidad_restante <= 0:
                break
            if registro['cantidad'] > cantidad_restante:
                # Si el registro tiene más cantidad que la que queremos restar
                nuevo_stock = registro['cantidad'] - cantidad_restante
                cursor.execute("UPDATE maplets_armados SET cantidad = ? WHERE id = ?", (nuevo_stock, registro['id']))
                cantidad_restante = 0
            else:
                # Si el registro tiene menos cantidad que la que queremos restar
                cursor.execute("UPDATE maplets_armados SET cantidad = 0 WHERE id = ?", (registro['id'],))
                cantidad_restante -= registro['cantidad']

        conn.commit()
        conn.close()
        return redirect(url_for('venta_maplets'))

    # Obtener historial de ventas
    cursor.execute("SELECT * FROM ventas_maplets")
    ventas_maplets = cursor.fetchall()
    conn.close()

    return render_template('venta_maplets.html', ventas_maplets=ventas_maplets)


@app.route('/venta_cajas', methods=['GET', 'POST'])
def venta_cajas():
    conn = sqlite3.connect('campo_libre.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == 'POST':
        vendedor = request.form['vendedor']
        fecha = request.form['fecha']
        cantidad_cajas = int(request.form['cantidad_cajas'])

        # Verificar existencia de stock para cajas
        cursor.execute("SELECT SUM(cantidad) AS total_cajas FROM cajas_armadas")
        stock_cajas = cursor.fetchone()['total_cajas']

        # Si hay suficiente stock, registrar la venta
        if stock_cajas >= cantidad_cajas:
            # Registrar venta de cajas
            cursor.execute("INSERT INTO ventas_cajas (vendedor, cantidad, fecha) VALUES (?, ?, ?)",
                           (vendedor, cantidad_cajas, fecha))

            # Actualizar el stock de cajas
            cursor.execute("UPDATE cajas_armadas SET cantidad = cantidad - ? WHERE id = 1", (cantidad_cajas,))

            conn.commit()
            conn.close()
            return redirect(url_for('venta_cajas'))
        else:
            conn.close()
            return "Error: No hay suficiente stock de cajas para vender."

    # Obtener historial de ventas de cajas
    cursor.execute("SELECT * FROM ventas_cajas")
    ventas_cajas = cursor.fetchall()
    conn.close()

    return render_template('venta_cajas.html', ventas_cajas=ventas_cajas)






@app.route('/stock_maplets_cajas', methods=['GET'])
def stock_maplets_cajas():
    conn = sqlite3.connect('campo_libre.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Obtener el total de maplets agrupados por categoria
    cursor.execute("SELECT categoria, SUM(cantidad) AS total_maplets FROM maplets_armados GROUP BY categoria")
    maplets = cursor.fetchall()

    # Obtener el total de cajas
    cursor.execute("SELECT SUM(cantidad) AS total_cajas FROM cajas_armadas")
    cajas = cursor.fetchone()

    conn.close()
    return render_template('stock_maplets_cajas.html', maplets=maplets, cajas=cajas)




@app.route('/reportes', methods=['GET', 'POST'])
def reportes():
    if request.method == 'POST':
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        vendedor = request.form.get('vendedor', None)

        conn = sqlite3.connect('campo_libre.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Obtener ventas de maplets
        query_maplets = """
            SELECT * FROM ventas_maplets
            WHERE fecha BETWEEN ? AND ?
        """
        params_maplets = (fecha_inicio, fecha_fin)
        if vendedor:
            query_maplets += " AND vendedor LIKE ?"
            params_maplets = (fecha_inicio, fecha_fin, f"%{vendedor}%")
        cursor.execute(query_maplets, params_maplets)
        ventas_maplets = cursor.fetchall()

        # Obtener ventas de cajas
        query_cajas = """
            SELECT * FROM ventas_cajas
            WHERE fecha BETWEEN ? AND ?
        """
        params_cajas = (fecha_inicio, fecha_fin)
        if vendedor:
            query_cajas += " AND vendedor LIKE ?"
            params_cajas = (fecha_inicio, fecha_fin, f"%{vendedor}%")
        cursor.execute(query_cajas, params_cajas)
        ventas_cajas = cursor.fetchall()

        # Obtener carros y gallinas
        query_carros = "SELECT * FROM gallinas_carro"
        cursor.execute(query_carros)
        carros = cursor.fetchall()

        # Obtener recolecciones
        query_recolecciones = "SELECT * FROM recolecciones WHERE fecha BETWEEN ? AND ?"
        cursor.execute(query_recolecciones, (fecha_inicio, fecha_fin))
        recolecciones = cursor.fetchall()

        # Calcular porcentaje de postura por carro
        postura_por_carro = []
        for carro in carros:
            cantidad_gallinas = carro['cantidad_gallinas']
            # Consultar cantidad de huevos recolectados por carro
            cursor.execute("""
                SELECT SUM(cantidad_huevos) AS total_huevos
                FROM recolecciones
                WHERE carro = ?
            """, (carro['carro'],))
            resultado_huevos = cursor.fetchone()
            cantidad_huevos = resultado_huevos['total_huevos'] if resultado_huevos else 0
            porcentaje_postura = (cantidad_huevos / cantidad_gallinas) * 100 if cantidad_gallinas else 0
            postura_por_carro.append({
                'carro': carro['carro'],
                'cantidad_gallinas': cantidad_gallinas,
                'cantidad_huevos': cantidad_huevos,
                'porcentaje_postura': round(porcentaje_postura, 2)
            })

        # Obtener stock total
        query_stock_total = "SELECT * FROM stock_total WHERE fecha_actualizacion BETWEEN ? AND ?"
        cursor.execute(query_stock_total, (fecha_inicio, fecha_fin))
        stock_total = cursor.fetchall()

        # Obtener armado de maplets y cajas
        query_armado = "SELECT * FROM armado WHERE fecha BETWEEN ? AND ?"
        cursor.execute(query_armado, (fecha_inicio, fecha_fin))
        armado = cursor.fetchall()

        # Obtener maplets armados
        query_maplets_armados = "SELECT * FROM maplets_armados WHERE fecha BETWEEN ? AND ?"
        cursor.execute(query_maplets_armados, (fecha_inicio, fecha_fin))
        maplets_armados = cursor.fetchall()

        # Obtener cajas armadas
        query_cajas_armadas = "SELECT * FROM cajas_armadas WHERE fecha BETWEEN ? AND ?"
        cursor.execute(query_cajas_armadas, (fecha_inicio, fecha_fin))
        cajas_armadas = cursor.fetchall()

        conn.close()

        return render_template(
            'reportes.html',
            ventas_maplets=ventas_maplets, ventas_cajas=ventas_cajas,
            carros=carros, recolecciones=recolecciones, stock_total=stock_total,
            armado=armado, maplets_armados=maplets_armados, cajas_armadas=cajas_armadas,
            fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, vendedor=vendedor,
            postura_por_carro=postura_por_carro
        )

    return render_template('reportes.html')

@app.route('/exportar_reportes', methods=['POST'])
def exportar_reportes():
    fecha_inicio = request.form['fecha_inicio']
    fecha_fin = request.form['fecha_fin']
    vendedor = request.form.get('vendedor', None)

    conn = sqlite3.connect('campo_libre.db')

    # Consultar ventas de maplets
    query_maplets = """
        SELECT fecha, vendedor, categoria, cantidad
        FROM ventas_maplets
        WHERE fecha BETWEEN ? AND ?
    """
    params_maplets = (fecha_inicio, fecha_fin)
    if vendedor:
        query_maplets += " AND vendedor LIKE ?"
        params_maplets = (fecha_inicio, fecha_fin, f"%{vendedor}%")
    df_maplets = pd.read_sql_query(query_maplets, conn, params=params_maplets)

    # Consultar ventas de cajas
    query_cajas = """
        SELECT fecha, vendedor, cantidad, 'N/A' AS categoria
        FROM ventas_cajas
        WHERE fecha BETWEEN ? AND ?
    """
    params_cajas = (fecha_inicio, fecha_fin)
    if vendedor:
        query_cajas += " AND vendedor LIKE ?"
        params_cajas = (fecha_inicio, fecha_fin, f"%{vendedor}%")
    df_cajas = pd.read_sql_query(query_cajas, conn, params=params_cajas)

    # Consultar carros y cantidad de gallinas
    query_carros = """
        SELECT carro, cantidad_gallinas, fecha
        FROM gallinas_carro
    """
    df_carros = pd.read_sql_query(query_carros, conn)

    # Consultar recolecciones
    query_recolecciones = """
        SELECT carro, cantidad_huevos, huevos_rotos, turno, fecha
        FROM recolecciones
    """
    df_recolecciones = pd.read_sql_query(query_recolecciones, conn)

    # Consultar stock total
    query_stock_total = """
        SELECT cantidad_huevos, fecha_actualizacion
        FROM stock_total
    """
    df_stock_total = pd.read_sql_query(query_stock_total, conn)

    # Consultar datos de armado (maplets y cajas)
    query_armado = """
        SELECT tipo, categoria, cantidad, fecha
        FROM armado
        WHERE fecha BETWEEN ? AND ?
    """
    df_armado = pd.read_sql_query(query_armado, conn, params=(fecha_inicio, fecha_fin))

    # Consultar maplets armados
    query_maplets_armados = """
        SELECT categoria, cantidad, fecha
        FROM maplets_armados
        WHERE fecha BETWEEN ? AND ?
    """
    df_maplets_armados = pd.read_sql_query(query_maplets_armados, conn, params=(fecha_inicio, fecha_fin))

    # Consultar cajas armadas
    query_cajas_armadas = """
        SELECT cantidad, fecha
        FROM cajas_armadas
        WHERE fecha BETWEEN ? AND ?
    """
    df_cajas_armadas = pd.read_sql_query(query_cajas_armadas, conn, params=(fecha_inicio, fecha_fin))

    # Consultar el porcentaje de postura de gallinas
    query_posturas = """
        SELECT gallinas_carro.carro, gallinas_carro.cantidad_gallinas, SUM(recolecciones.cantidad_huevos) AS total_huevos
        FROM gallinas_carro
        LEFT JOIN recolecciones ON gallinas_carro.carro = recolecciones.carro
        GROUP BY gallinas_carro.carro
    """
    df_posturas = pd.read_sql_query(query_posturas, conn)

    # Calcular el porcentaje de postura
    df_posturas['porcentaje_postura'] = (df_posturas['total_huevos'] / df_posturas['cantidad_gallinas']) * 100

    conn.close()

    # Escribir los DataFrames a un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_maplets.to_excel(writer, sheet_name='Ventas Maplets', index=False)
        df_cajas.to_excel(writer, sheet_name='Ventas Cajas', index=False)
        df_carros.to_excel(writer, sheet_name='Carros y Gallinas', index=False)
        df_recolecciones.to_excel(writer, sheet_name='Recolecciones', index=False)
        df_stock_total.to_excel(writer, sheet_name='Stock Total', index=False)
        df_armado.to_excel(writer, sheet_name='Armado (Maplets y Cajas)', index=False)
        df_maplets_armados.to_excel(writer, sheet_name='Maplets Armados', index=False)
        df_cajas_armadas.to_excel(writer, sheet_name='Cajas Armadas', index=False)
        df_posturas.to_excel(writer, sheet_name='Porcentaje de Postura', index=False)

    output.seek(0)

    # Enviar el archivo Excel como respuesta
    return send_file(output, as_attachment=True, download_name="reporte_completo.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.route('/posturas')
def posturas():
    conn = sqlite3.connect('campo_libre.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Obtener la cantidad de gallinas por carro
    cursor.execute("""
        SELECT carro, cantidad_gallinas
        FROM gallinas_carro
    """)
    gallinas_por_carro = cursor.fetchall()

    # Obtener los huevos recolectados por carro
    cursor.execute("""
        SELECT carro, SUM(cantidad_huevos) AS total_huevos
        FROM recolecciones
        GROUP BY carro
    """)
    huevos_por_carro = cursor.fetchall()

    # Crear un diccionario para almacenar los datos de gallinas y huevos
    gallinas_dict = {g['carro']: g['cantidad_gallinas'] for g in gallinas_por_carro}
    huevos_dict = {h['carro']: h['total_huevos'] for h in huevos_por_carro}

    # Calcular el porcentaje de postura por carro
    posturas = []
    for carro, cantidad_gallinas in gallinas_dict.items():
        cantidad_huevos = huevos_dict.get(carro, 0)
        porcentaje_postura = (cantidad_huevos / cantidad_gallinas) * 100 if cantidad_gallinas else 0
        posturas.append({
            'carro': carro,
            'cantidad_gallinas': cantidad_gallinas,
            'cantidad_huevos': cantidad_huevos,
            'porcentaje_postura': round(porcentaje_postura, 2)
        })

    conn.close()

    return render_template('posturas.html', posturas=posturas)






@app.route('/stock')
def stock():
    conn = sqlite3.connect('campo_libre.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Obtener el valor consolidado de stock_total
    cursor.execute("SELECT SUM(cantidad_huevos) AS total_huevos FROM stock_total")
    stock_huevos_row = cursor.fetchone()

    # Usar el nombre correcto de la columna (total_huevos) o asignar 0 si no hay datos
    stock_huevos = stock_huevos_row['total_huevos'] if stock_huevos_row and stock_huevos_row['total_huevos'] is not None else 0

    # Obtener el stock de maplets
    cursor.execute("SELECT categoria, SUM(cantidad) AS total_maplets FROM maplets_armados GROUP BY categoria")
    maplets = cursor.fetchall()

    # Obtener el stock de cajas
    cursor.execute("SELECT SUM(cantidad) AS total_cajas FROM cajas_armadas")
    cajas = cursor.fetchone()

    conn.close()

    return render_template(
        'stock.html',
        stock_huevos={'total_huevos': stock_huevos},  # Pasar como un diccionario para el HTML
        maplets=maplets,
        cajas=cajas
    )
    
    
@app.route('/ventas', methods=['GET', 'POST'])
def ventas():
    conn = sqlite3.connect('campo_libre.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == 'POST':
        if "venta_maplets" in request.form:
            # Procesar venta de maplets
            vendedor = request.form['vendedor']
            fecha = request.form['fecha']
            categoria_maplet = request.form['categoria_maplet']
            cantidad_maplets = int(request.form['cantidad_maplets'])

            # Verificar el stock de maplets por categoría
            cursor.execute("SELECT cantidad FROM maplets_armados WHERE categoria = ?", (categoria_maplet,))
            maplet_stock = cursor.fetchone()

            if not maplet_stock or maplet_stock['cantidad'] < cantidad_maplets:
                conn.close()
                return f"Error: No hay suficiente stock de maplets en la categoría '{categoria_maplet}'. Disponibles: {maplet_stock['cantidad'] if maplet_stock else 0}"

            # Registrar la venta de maplets
            cursor.execute("INSERT INTO ventas_maplets (vendedor, categoria, cantidad, fecha) VALUES (?, ?, ?, ?)",
                           (vendedor, categoria_maplet, cantidad_maplets, fecha))

            # Restar del stock de maplets
            nuevo_stock_maplets = maplet_stock['cantidad'] - cantidad_maplets
            cursor.execute("UPDATE maplets_armados SET cantidad = ? WHERE categoria = ?", (nuevo_stock_maplets, categoria_maplet))

        elif "venta_cajas" in request.form:
            # Procesar venta de cajas
            vendedor = request.form['vendedor']
            fecha = request.form['fecha']
            cantidad_cajas = int(request.form['cantidad_cajas'])

            # Verificar el stock total de cajas
            cursor.execute("SELECT SUM(cantidad) AS total_cajas FROM cajas_armadas")
            total_cajas_disponibles = cursor.fetchone()
            total_cajas_disponibles = total_cajas_disponibles['total_cajas'] if total_cajas_disponibles else 0

            if total_cajas_disponibles < cantidad_cajas:
                conn.close()
                return f"Error: No hay suficiente stock de cajas. Disponibles: {total_cajas_disponibles}"

            # Registrar la venta de cajas
            cursor.execute("INSERT INTO ventas_cajas (vendedor, cantidad, fecha) VALUES (?, ?, ?)",
                           (vendedor, cantidad_cajas, fecha))

            # Restar del stock de cajas armadas
            cursor.execute("SELECT id, cantidad FROM cajas_armadas WHERE cantidad > 0 ORDER BY fecha ASC")
            cajas_armadas = cursor.fetchall()

            cantidad_restante = cantidad_cajas
            for caja in cajas_armadas:
                if cantidad_restante <= 0:
                    break

                if caja['cantidad'] <= cantidad_restante:
                    cantidad_restante -= caja['cantidad']
                    cursor.execute("UPDATE cajas_armadas SET cantidad = 0 WHERE id = ?", (caja['id'],))
                else:
                    nuevo_stock_cajas = caja['cantidad'] - cantidad_restante
                    cursor.execute("UPDATE cajas_armadas SET cantidad = ? WHERE id = ?", (nuevo_stock_cajas, caja['id']))
                    cantidad_restante = 0

        conn.commit()
        conn.close()
        return redirect(url_for('ventas'))

    # Consultar el historial de ventas de maplets
    cursor.execute("SELECT * FROM ventas_maplets")
    ventas_maplets = cursor.fetchall()

    # Consultar el historial de ventas de cajas
    cursor.execute("SELECT * FROM ventas_cajas")
    ventas_cajas = cursor.fetchall()

    # Consultar el stock de maplets
    cursor.execute("SELECT categoria, cantidad FROM maplets_armados")
    stock_maplets = cursor.fetchall()

    # Consultar el stock de cajas
    cursor.execute("SELECT SUM(cantidad) AS total_cajas FROM cajas_armadas")
    stock_cajas_row = cursor.fetchone()
    stock_cajas = stock_cajas_row['total_cajas'] if stock_cajas_row else 0

    conn.close()

    return render_template('ventas.html', ventas_maplets=ventas_maplets, ventas_cajas=ventas_cajas, stock_maplets=stock_maplets, stock_cajas=stock_cajas)





@app.route('/reset-database', methods=['POST'])
def reset_database():
    conn = sqlite3.connect('campo_libre.db')
    cursor = conn.cursor()
    try:
        # Lista de tablas a borrar
        tables = [
            'recolecciones', 'armado', 'armados', 'cajas_armadas',
            'gallinas_carro', 'maplets_armados', 'stock', 'stock_total',
            'ventas', 'ventas_cajas', 'ventas_maplets'
        ]

        # Borrar contenido de cada tabla
        for table in tables:
            cursor.execute(f"DELETE FROM {table};")

        conn.commit()
        return jsonify({'message': 'Base de datos restablecida con éxito.'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'message': f'Error al restablecer la base de datos: {str(e)}'}), 500
    finally:
        conn.close()






if __name__ == '__main__':
    app.run(debug=True)
