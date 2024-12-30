import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_file
from datetime import datetime
import matplotlib
matplotlib.use('Agg') 
import pandas as pd  
import matplotlib.pyplot as plt
import io


app = Flask(__name__)

# Función para conectar con la base de datos
def get_db_connection():
    conn = sqlite3.connect('campo_libre.db')
    conn.row_factory = sqlite3.Row
    return conn

# Ruta de inicio para probar que Flask funciona
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para gestionar las recolecciones


@app.route('/recolecciones', methods=['GET', 'POST'])
def recolecciones():
    conn = get_db_connection()

    # Manejar el registro de recolecciones
    if request.method == 'POST':
        carro = request.form['carro']
        categoria = request.form['categoria']
        cantidad = int(request.form['cantidad'])
        turno = request.form['turno']
        fecha = request.form['fecha']  # Obtener la fecha del formulario

        # Insertar en
        # la tabla recolecciones
        conn.execute(
            'INSERT INTO recolecciones (carro, categoria, cantidad, turno, fecha) VALUES (?, ?, ?, ?, ?)',
            (carro, categoria, cantidad, turno, fecha)
        )

        # Actualizar el stock
        conn.execute(
            'UPDATE stock SET total_huevos = total_huevos + ? WHERE categoria = ?',
            (cantidad, categoria)
        )

        conn.commit()
        conn.close()
        return redirect(url_for('recolecciones'))

    # Manejar el filtro de fecha
    fecha_filtro = request.args.get('fecha', datetime.now().strftime('%Y-%m-%d'))
    recolecciones = conn.execute(
        # Cambiamos el ORDER BY para incluir turno y fecha en orden descendente
        'SELECT * FROM recolecciones WHERE fecha = ? ORDER BY fecha DESC',
        (fecha_filtro,)
    ).fetchall()
    conn.close()
    recolecciones = sorted(recolecciones, key=lambda x: (x['fecha'], x['turno']), reverse=True)
    return render_template('recolecciones.html', recolecciones=recolecciones, fecha_filtro=fecha_filtro)

# Ruta para gestionar las ventas
from datetime import datetime

@app.route('/ventas', methods=['GET', 'POST'])
def ventas():
    conn = get_db_connection()
    mensaje = None

    # Manejo del formulario de ventas
    if request.method == 'POST':
        vendedor = request.form['vendedor']
        categoria = request.form['categoria']
        maplets = int(request.form['maplets'])
        cajas = int(request.form['cajas'])
        fecha = request.form.get('fecha', datetime.now().strftime('%Y-%m-%d'))

        huevos_necesarios = maplets * 30 + cajas * 6

        stock = conn.execute(
            'SELECT total_huevos FROM stock WHERE categoria = ?', (categoria,)
        ).fetchone()

        if stock and stock['total_huevos'] >= huevos_necesarios:
            conn.execute(
                'UPDATE stock SET total_huevos = total_huevos - ? WHERE categoria = ?',
                (huevos_necesarios, categoria)
            )
            conn.execute(
                'INSERT INTO ventas (vendedor, categoria, maplets, cajas, fecha) VALUES (?, ?, ?, ?, ?)',
                (vendedor, categoria, maplets, cajas, fecha)
            )
            mensaje = "Venta registrada con éxito."
            conn.commit()
        else:
            mensaje = "No hay suficiente stock para completar la venta."
            conn.rollback()

    # Obtener el historial de ventas
    ventas = conn.execute('SELECT * FROM ventas').fetchall()

    # Obtener el resumen de stock
    stock = conn.execute('SELECT * FROM stock').fetchall()
    conn.close()

    return render_template('ventas.html', ventas=ventas, stock=stock, mensaje=mensaje, datetime=datetime)





@app.route('/resumen', methods=['GET', 'POST'])
def resumen():
    conn = get_db_connection()
    mensaje = None

    if request.method == 'POST':
        # Obtener datos del formulario
        vendedor = request.form['vendedor']
        categoria = request.form['categoria']
        maplets = int(request.form['maplets'])
        cajas = int(request.form['cajas'])
        fecha = request.form.get('fecha', datetime.now().strftime('%Y-%m-%d'))  # Fecha del formulario o actual

        # Calcular huevos necesarios
        huevos_necesarios = maplets * 30 + cajas * 6

        # Verificar el stock disponible
        stock = conn.execute(
            'SELECT total_huevos FROM stock WHERE categoria = ?', (categoria,)
        ).fetchone()

        if stock and stock['total_huevos'] >= huevos_necesarios:
            # Actualizar el stock si hay suficiente
            conn.execute(
                'UPDATE stock SET total_huevos = total_huevos - ? WHERE categoria = ?',
                (huevos_necesarios, categoria)
            )
            # Registrar la venta
            conn.execute(
                'INSERT INTO ventas (vendedor, categoria, maplets, cajas, fecha) VALUES (?, ?, ?, ?, ?)',
                (vendedor, categoria, maplets, cajas, fecha)
            )
            conn.commit()
            mensaje = "Venta registrada con éxito."
        else:
            # No realizar cambios si no hay suficiente stock
            mensaje = f"No hay suficiente stock para completar la venta. Stock actual: {stock['total_huevos']} unidades."

    # Mostrar el stock actual
    stock = conn.execute('SELECT * FROM stock').fetchall()
    conn.close()
    return render_template('resumen.html', stock=stock, mensaje=mensaje, datetime=datetime)




@app.route('/ajustar_stock', methods=['POST'])
def ajustar_stock():
    conn = get_db_connection()

    # Obtener datos del formulario
    categoria = request.form['categoria']
    ajuste = int(request.form['ajuste'])

    # Consultar el stock actual
    stock = conn.execute(
        'SELECT total_huevos FROM stock WHERE categoria = ?', (categoria,)
    ).fetchone()

    if stock and stock['total_huevos'] + ajuste < 0:
        # Si el ajuste hace que el stock sea negativo, mostrar mensaje de error
        mensaje = f"No se puede ajustar el stock. Stock actual: {stock['total_huevos']} unidades."
    else:
        # Realizar el ajuste de stock
        conn.execute(
            'UPDATE stock SET total_huevos = total_huevos + ? WHERE categoria = ?',
            (ajuste, categoria)
        )
        conn.commit()
        mensaje = "El stock ha sido ajustado correctamente."

    conn.close()
    return redirect(url_for('resumen', mensaje=mensaje))



@app.route('/reportes', methods=['GET', 'POST'])
def reportes():
    conn = get_db_connection()
    query = "SELECT * FROM ventas"
    filters = []
    vendedor = None
    categoria = None
    fecha_inicio = None
    fecha_fin = None
    reportes = []
    vendedores = conn.execute("SELECT DISTINCT vendedor FROM ventas").fetchall()

    if request.method == 'POST':
        # Obtener filtros del formulario
        vendedor = request.form.get('vendedor')
        categoria = request.form.get('categoria')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')

        # Construir la consulta con filtros
        if vendedor and vendedor != "Todos":
            filters.append(f"vendedor = '{vendedor}'")
        if categoria and categoria != "Todas":
            filters.append(f"categoria = '{categoria}'")
        if fecha_inicio and fecha_fin:
            filters.append(f"fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'")

        if filters:
            query += " WHERE " + " AND ".join(filters)

        reportes = conn.execute(query).fetchall()

        # Generar gráfico si hay reportes
        if reportes:
            total_maplets = sum(row['maplets'] for row in reportes)
            total_cajas = sum(row['cajas'] for row in reportes)

            # Verificar que haya ventas en al menos una categoría
            if total_maplets == 0 and total_cajas == 0:
                sizes = [0, 0]  # Si no hay datos, evitar dividir por cero
            else:
                sizes = [total_maplets, total_cajas]

            # Ajustar para que los porcentajes reflejen solo las ventas reales
            total_ventas = sum(sizes)
            if total_ventas > 0:
                sizes = [(count / total_ventas) * 100 for count in sizes]

            labels = ['Maplets', 'Cajas']
            colors = ['blue', 'orange']
            explode = (0.1, 0)  # Resaltar el segmento de maplets

            plt.figure(figsize=(6, 6))
            plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
            plt.axis('equal')  # Asegura que sea un círculo perfecto
            plt.savefig('static/images/ventas_pie_chart.png')
            plt.close()

    conn.close()

    return render_template(
        'reportes.html',
        reportes=reportes,
        vendedores=vendedores,
        vendedor=vendedor,
        categoria=categoria,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )


@app.route('/exportar_excel', methods=['POST'])
def exportar_excel():
    conn = get_db_connection()
    query = "SELECT * FROM ventas"
    filters = []

    # Obtener filtros del formulario
    vendedor = request.form.get('vendedor')
    categoria = request.form.get('categoria')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')

    if vendedor and vendedor != "Todos":
        filters.append(f"vendedor = '{vendedor}'")
    if categoria and categoria != "Todas":
        filters.append(f"categoria = '{categoria}'")
    if fecha_inicio and fecha_fin:
        filters.append(f"fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'")

    if filters:
        query += " WHERE " + " AND ".join(filters)

    # Consultar los datos filtrados
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Exportar los datos filtrados a Excel
    file_path = "reportes_ventas_filtradas.xlsx"
    df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)



@app.route('/ver_grafico', methods=['POST'])
def ver_grafico():
    conn = get_db_connection()
    query = "SELECT * FROM ventas"
    filters = []
    vendedor = request.form.get('vendedor')
    categoria = request.form.get('categoria')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')

    # Construir la consulta con filtros
    if vendedor and vendedor != "Todos":
        filters.append(f"vendedor = '{vendedor}'")
    if categoria and categoria != "Todas":
        filters.append(f"categoria = '{categoria}'")
    if fecha_inicio and fecha_fin:
        filters.append(f"fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'")

    if filters:
        query += " WHERE " + " AND ".join(filters)

    reportes = conn.execute(query).fetchall()
    conn.close()

    # Generar gráfico
    total_maplets = sum(row['maplets'] for row in reportes)
    total_cajas = sum(row['cajas'] for row in reportes)

    # Verificar que haya ventas en al menos una categoría
    sizes = [total_maplets, total_cajas]
    total_ventas = sum(sizes)

    if total_ventas > 0:
        labels = ['Maplets', 'Cajas']
        colors = ['#E6A75F', '#4DBF6D']
        sizes = [78.6, 21.4]
        explode = (0.1, 0)  # Resaltar el segmento de maplets

        plt.figure(figsize=(6, 6))
        plt.pie(sizes, explode=explode,textprops={'fontsize': 20} , labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')  # Asegura que sea un círculo perfecto
        plt.savefig('static/images/ventas_pie_chart.png')
        plt.close()

    return render_template(
        'reportes.html',
        reportes=reportes,
        vendedor=vendedor,
        categoria=categoria,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        graph_path='static/images/ventas_pie_chart.png'
    )


if __name__ == '__main__':
    app.run(debug=True)