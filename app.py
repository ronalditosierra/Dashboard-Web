from flask import Flask, render_template, request, redirect, url_for, flash, session,send_file
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import pandas as pd
import sqlite3
import json
from datetime import datetime
import io
import xlsxwriter

base_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            template_folder=os.path.join(base_dir, 'FrontEnd', 'Templates'), 
            static_folder=os.path.join(base_dir, 'FrontEnd', 'Static'))
app.secret_key = "supersecretkey"

if os.environ.get('VERCEL'):
    UPLOAD_FOLDER = '/tmp'
else:
    UPLOAD_FOLDER = os.path.join('FrontEnd', 'Static', 'Uploads')

if not os.environ.get('VERCEL'):
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

DATABASE = 'logistica.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# --- DASHBOARD Y GESTIÓN DE TABLAS ---
@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    tabla_seleccionada = request.args.get('tabla')
    conn = get_db_connection()
    
    totales = {
        'empleados': conn.execute('SELECT COUNT(*) FROM Empleados').fetchone()[0],
        'vehiculos': conn.execute('SELECT COUNT(*) FROM Vehiculos').fetchone()[0],
        'rutas': conn.execute('SELECT COUNT(*) FROM Rutas').fetchone()[0],
        'clientes': conn.execute('SELECT COUNT(*) FROM Clientes').fetchone()[0]
    }

    if not tabla_seleccionada:
        ingresos_res = conn.execute('SELECT SUM(Monto) FROM Facturas WHERE Estado="Pagada"').fetchone()
        ingresos_total = ingresos_res[0] if ingresos_res[0] else 0

        cargas_raw = conn.execute('SELECT Tipo_Carga, COUNT(*) as cant FROM Cargas GROUP BY Tipo_Carga').fetchall()
        chart_cargas = {
            'labels': [row['Tipo_Carga'] for row in cargas_raw],
            'values': [row['cant'] for row in cargas_raw]
        }

        facturas_raw = conn.execute('SELECT Fecha, SUM(Monto) as total FROM Facturas GROUP BY Fecha ORDER BY Fecha ASC').fetchall()
        chart_ingresos = {
            'labels': [row['Fecha'] for row in facturas_raw],
            'values': [row['total'] for row in facturas_raw]
        }

        recientes = conn.execute('''
            SELECT f.ID_Factura, c.Nombre, f.Monto, f.Estado 
            FROM Facturas f 
            JOIN Clientes c ON f.ID_Cliente = c.ID_Cliente 
            ORDER BY f.ID_Factura DESC LIMIT 4
        ''').fetchall()

        conn.close()
        return render_template('index.html', vista ='dashboard',
                               es_dashboard=True, totales=totales, ingresos=ingresos_total,
                               recientes=recientes, chart_cargas=json.dumps(chart_cargas),
                               chart_ingresos=json.dumps(chart_ingresos), tabla_activa='Centro de Control')

    else:
        datos_tabla = []
        columnas = []
        try:
            cursor = conn.execute(f'SELECT * FROM {tabla_seleccionada}')
            datos_tabla = [list(row) for row in cursor.fetchall()]
            columnas = [desc[0] for desc in cursor.description]
        except Exception as e: print(f"Error: {e}")
        
        conn.close()
        return render_template('index.html', es_dashboard=False, datos_tabla=datos_tabla, 
                               columnas=columnas, totales=totales, tabla_activa=tabla_seleccionada)

# --- PROCESAMIENTO DE ARCHIVOS EXCEL XLSX Y CSV ---
@app.route('/upload_file', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if file and file.filename != '':
        filepath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(filepath)
        try:
            excel_data = pd.read_excel(filepath, sheet_name=None)
            conn = sqlite3.connect(DATABASE)
            # Lista de tus 8 tablas
            tablas_validas = ['Usuario', 'Empleados', 'Vehiculos', 'Rutas', 'Clientes', 'Cargas', 'Facturas', 'Proveedores', 'Gastos']
            for hoja, df in excel_data.items():
                if hoja.strip() in tablas_validas:
                    df.to_sql(hoja.strip(), conn, if_exists='append', index=False)
            conn.commit()
            conn.close()
            os.remove(filepath)
            flash('¡Base de datos alimentada correctamente!', 'success')
        except Exception as e: flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('index'))

# --- LOGIN / LOGOUT ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo, password = request.form.get('correo'), request.form.get('password')
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM Usuario WHERE Correo = ?', (correo,)).fetchone()
        conn.close()
        if user and check_password_hash(user['Contrasena'], password):
            session.update({'user_id': user['IDUsuario'], 'user_name': f"{user['Nombres']} {user['Apellidos']}", 'user_role': user['Rol']})
            return redirect(url_for('index'))
        flash('Credenciales inválidas', 'danger')
    return render_template('Auth/login.html')

# ---- REGISTRO ----
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        correo = request.form.get('correo')
        password = request.form.get('password')
        rol = request.form.get('rol', 'Usuario')

        if not correo or not password:
            flash('Correo y contraseña son obligatorios', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            existe = conn.execute('SELECT IDUsuario FROM Usuario WHERE Correo = ?', (correo,)).fetchone()
            if existe:
                flash('El correo ya está registrado', 'warning')
                return redirect(url_for('register'))
                        
            conn.execute('''
                INSERT INTO Usuario (Nombres, Apellidos, Correo, Contrasena, Rol) 
                VALUES (?, ?, ?, ?, ?)
            ''', (nombres, apellidos, correo, hashed_password, rol))
            conn.commit()
            
            flash('Cuenta creada con éxito. ¡Ahora puedes iniciar sesión!', 'success')
            return redirect(url_for('login'))
        
        except Exception as e:
            print(f"Error en registro: {e}")
            flash('Error interno al crear la cuenta', 'danger')
        finally:
            conn.close()

    return render_template('Auth/register.html')
            
#---- CERRAR SESION ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

 # --- PAGINA EMPLEADOS Y VEHICULOS ---           
@app.route('/activos_internos')
def activos_internos():
    if 'user_id' not in session: 
        return redirect(url_for('login'))
    
    tipo = request.args.get('tipo', 'personal')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    conn = get_db_connection()
    datos_tabla = []
    columnas_tabla = []
    total_records = 0
    cursor = conn.cursor()
    cursor.execute("SELECT Cargo, COUNT(*) FROM Empleados GROUP BY Cargo")
    res_emp = cursor.fetchall()
    chart_emp = {
        "labels": [row[0] for row in res_emp],
        "values": [row[1] for row in res_emp]
    }

    cursor.execute("SELECT Marca, COUNT(*) FROM Vehiculos GROUP BY Marca")
    res_veh = cursor.fetchall()
    chart_veh = {
        "labels": [row[0] for row in res_veh],
        "values": [row[1] for row in res_veh]
    }
    try:
        if tipo == 'personal':
            total_records = conn.execute('SELECT COUNT(*) FROM Empleados').fetchone()[0]
            cursor = conn.execute('SELECT ID_Empleado, Nombre, Apellido, Cargo, Telefono FROM Empleados LIMIT ? OFFSET ?', (per_page, offset)).fetchall()
            columnas_tabla = ["Nombre", "Apellido", "Cargo", "Teléfono"]
        else:
            total_records = conn.execute('SELECT COUNT(*) FROM Vehiculos').fetchone()[0]
            cursor = conn.execute('SELECT ID_Vehiculo, Placa, Marca, Modelo, Tipo_Vehiculo, Anio, Capacidad_Carga FROM Vehiculos LIMIT ? OFFSET ?', (per_page, offset)).fetchall()
            columnas_tabla = ["Placa", "Marca", "Modelo", "Tipo Vehículo", "Año","Capacidad De Carga"]
        
        datos_tabla = [list(row) for row in cursor]
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

    total_pages = (total_records + per_page - 1) // per_page
    
    
    return render_template('activos_internos.html', 
                           vista='activos', tipo=tipo, 
                           datos=datos_tabla, columnas=columnas_tabla,
                           page=page, total_pages=total_pages, total_records=total_records,
                           chart_emp=chart_emp, chart_veh=chart_veh)
            
#--- BOTON DE ELIMINAR ---
@app.route('/eliminar_activo/<tipo>/<id>')
def eliminar_activo(tipo, id):
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    
    mapeo = {
        'personal': ('Empleados', 'ID_Empleado'),
        'vehiculos': ('Vehiculos', 'ID_Vehiculo'),
        'clientes': ('Clientes', 'ID_Cliente'),
        'cargas': ('Cargas', 'ID_Carga'),
        'rutas': ('Rutas', 'ID_Ruta')
    }

    if tipo in mapeo:
        tabla, columna_id = mapeo[tipo]
        try:
            conn.execute(f'DELETE FROM {tabla} WHERE {columna_id} = ?', (id,))
            conn.commit()
            flash(f'Registro de {tipo} eliminado con éxito', 'success')
        except Exception as e:
            flash(f'Error al eliminar: {e}', 'danger')
    
    conn.close()
    if tipo in ['clientes', 'cargas', 'rutas']:
        return redirect(url_for('operaciones', tipo=tipo))
    return redirect(url_for('activos_internos', tipo=tipo))
            
#--- PAGINA DE OPERACIONES CLIENTES, RUTAS ---
@app.route('/operaciones')
def operaciones():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    tipo = request.args.get('tipo', 'rutas')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    conn = get_db_connection()
    
    kpis = {
        'peso_total': conn.execute('SELECT SUM(Peso) FROM Cargas').fetchone()[0] or 0,
        'valor_total': conn.execute('SELECT SUM(Valor_Carga) FROM Cargas').fetchone()[0] or 0,
        'distancia_promedio': conn.execute('SELECT AVG(Distancia) FROM Rutas').fetchone()[0] or 0
    }

    
    cargas_raw = conn.execute('SELECT Tipo_Carga, COUNT(*) as cant FROM Cargas GROUP BY Tipo_Carga').fetchall()
    chart_cargas = {
        'labels': [row['Tipo_Carga'] for row in cargas_raw],
        'values': [row['cant'] for row in cargas_raw]
    }

    
    rutas_costo = conn.execute('SELECT Destino, Costo_Transporte FROM Rutas ORDER BY Costo_Transporte DESC LIMIT 5').fetchall()
    chart_rutas = {
        'labels': [row['Destino'] for row in rutas_costo],
        'values': [row['Costo_Transporte'] for row in rutas_costo]
    }

    datos_tabla = []
    columnas_tabla = []
    total_records = 0
    if tipo == 'clientes':
        total_records = conn.execute('SELECT COUNT(*) FROM Clientes').fetchone()[0]
        cursor = conn.execute('SELECT ID_Cliente AS id, Nombre, Email FROM Clientes LIMIT ? OFFSET ?', (per_page, offset)).fetchall()
        columnas_tabla = ["Nombre del Cliente", "Correo Electrónico"]
    elif tipo == 'cargas':
        total_records = conn.execute('SELECT COUNT(*) FROM Cargas').fetchone()[0]
        cursor = conn.execute('SELECT ID_Carga AS id, Tipo_Carga, Peso, Valor_Carga FROM Cargas LIMIT ? OFFSET ?', (per_page, offset)).fetchall()
        columnas_tabla = ["Categoría de Carga", "Masa Total (kg)", "Valor Declarado ($)"]
    else: # Rutas
        total_records = conn.execute('SELECT COUNT(*) FROM Rutas').fetchone()[0]
        cursor = conn.execute('SELECT ID_Ruta AS id,Origen, Destino, Distancia, Costo_Transporte FROM Rutas LIMIT ? OFFSET ?', (per_page, offset)).fetchall()
        columnas_tabla = ["Ciudad Origen","Ciudad Destino", "Recorrido (km)", "Costo Operativo ($)"]
    datos_tabla = [list(row) for row in cursor]
    total_pages = (total_records + per_page - 1) // per_page
    conn.close()

    return render_template('operaciones.html', 
                           vista='operaciones', tipo=tipo, kpis=kpis,
                           chart_cargas=json.dumps(chart_cargas),
                           chart_rutas=json.dumps(chart_rutas),
                           datos=datos_tabla, columnas=columnas_tabla,
                           page=page, total_pages=total_pages, total_records=total_records)
#--- PAGINA COMERCIAL ---
@app.route('/gestion_comercial')
def gestion_comercial():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    mes_filtro = request.args.get('mes')
    conn = get_db_connection()
    
    query_where = "WHERE Fecha LIKE ?" if mes_filtro else ""
    params = (f"2024-{mes_filtro}%",) if mes_filtro else ()

    ingresos = conn.execute(f'SELECT SUM(Monto) FROM Facturas {query_where}', params).fetchone()[0] or 0
    gastos = conn.execute(f'SELECT SUM(Monto) FROM Gastos {query_where}', params).fetchone()[0] or 0
    utilidad = ingresos - gastos
    margen = (utilidad / ingresos * 100) if ingresos > 0 else 0

    cobranza = conn.execute(f'SELECT Estado, SUM(Monto) as total FROM Facturas {query_where} GROUP BY Estado', params).fetchall()
    chart_cobranza = {'labels': [r['Estado'] for r in cobranza], 'values': [r['total'] for r in cobranza]}

    top_clientes = conn.execute(f'''
        SELECT c.Nombre, SUM(f.Monto) as total FROM Facturas f 
        JOIN Clientes c ON f.ID_Cliente = c.ID_Cliente 
        {query_where} GROUP BY c.Nombre ORDER BY total DESC LIMIT 5
    ''', params).fetchall()
    chart_top_clientes = {'labels': [r['Nombre'] for r in top_clientes], 'values': [r['total'] for r in top_clientes]}

    meses_nombres = [("01", "Enero"), ("02", "Febrero"), ("03", "Marzo"), ("04", "Abril"), ("05", "Mayo"), ("06", "Junio"), 
                     ("07", "Julio"), ("08", "Agosto"), ("09", "Septiembre"), ("10", "Octubre"), ("11", "Noviembre"), ("12", "Diciembre")]

    conn.close()
    return render_template('gestion_comercial.html', vista='comercial', stats={'ingresos': ingresos, 'gastos': gastos, 'utilidad': utilidad, 'margen': margen}, 
                           chart_cobranza=json.dumps(chart_cobranza), chart_top_clientes=json.dumps(chart_top_clientes), 
                           mes_actual=mes_filtro, meses=meses_nombres)
            
#--- BOTON PARA EXPORTAR INFORMACION A UN EXCEL ---
@app.route('/exportar_comercial')
def exportar_comercial():
    mes_filtro = request.args.get('mes')
    conn = get_db_connection()
    query_where = "WHERE Fecha LIKE ?" if mes_filtro else ""
    params = (f"2024-{mes_filtro}%",) if mes_filtro else ()

    df_fac = pd.read_sql_query(f"SELECT * FROM Facturas {query_where}", conn, params=params)
    df_gas = pd.read_sql_query(f"SELECT * FROM Gastos {query_where}", conn, params=params)
    
    resumen_data = {
        'Concepto': ['Total Ingresos', 'Total Gastos', 'Utilidad Neta', 'Margen %'],
        'Valor': [df_fac['Monto'].sum(), df_gas['Monto'].sum(), df_fac['Monto'].sum() - df_gas['Monto'].sum(), 
                  ((df_fac['Monto'].sum() - df_gas['Monto'].sum()) / df_fac['Monto'].sum() * 100) if df_fac['Monto'].sum() > 0 else 0]
    }
    df_res = pd.DataFrame(resumen_data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_res.to_excel(writer, sheet_name='RESUMEN_FINANCIERO', index=False)
        df_fac.to_excel(writer, sheet_name='INGRESOS', index=False)
        df_gas.to_excel(writer, sheet_name='GASTOS', index=False)
    
    conn.close()
    output.seek(0)
    return send_file(output, download_name=f"Balance_{mes_filtro or 'Anual'}.xlsx", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
