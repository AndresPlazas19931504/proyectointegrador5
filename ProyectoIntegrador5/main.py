import sqlite3, csv, os

# Configuración
DB_PATH, CSV_OUT = 'db/proyecto.db', 'db/export.csv'
DIRS, FILENAME = ['db', 'data'], 'Estadisticas_Riegos_Laborales_Positiva-Sep_2025.csv'
[os.makedirs(d, exist_ok=True) for d in DIRS]

# Buscar archivo o definir ruta por defecto
file_path = next((p for p in [os.path.join('data', FILENAME), FILENAME] if os.path.exists(p)), os.path.join('data', FILENAME))

def generar_dummy_si_no_existe():
    """Genera datos de prueba si el archivo no se encuentra."""
    if not os.path.exists(file_path):
        print("⚠️ Archivo no encontrado. Generando datos de prueba...")
        # Columnas simplificadas para el ejemplo
        cols = ['ACTIVEC', 'AÑO', 'ARL', 'DPTO', 'INC_AT', 'INC_EL', 'MES', 'MPIO', 'MUERTES', 'PEN_AT', 'PEN_EL', 'PRESUNTOS', 'DEP', 'INDEP']
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerows([cols, ['Construcción', '2023', 'ARL-1', 'Bogota', 0, 0, 'Enero', 'Bogota', 0, 0, 0, 10, 100, 20]])

def procesar_etl():
    """Ejecuta la extracción, transformación y carga (ETL)."""
    generar_dummy_si_no_existe()
    conn = sqlite3.connect(DB_PATH)
    
    # Intenta codificaciones comunes hasta que una funcione
    for enc in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with open(file_path, encoding=enc) as f:
                # Detectar dialecto y leer
                dialect = csv.Sniffer().sniff(f.read(1024)); f.seek(0)
                reader = csv.DictReader(f, dialect=dialect)
                headers = [h.strip() for h in reader.fieldnames]
                
                # *** 1. ELIMINAR Y CREAR TABLA PARA REINICIO COMPLETO (Actualización) ***
                conn.execute("DROP TABLE IF EXISTS reporte_arl")
                conn.execute(f"CREATE TABLE reporte_arl ({', '.join(h.replace(' ', '_') + ' TEXT' for h in headers)})")
                
                # Inserción masiva (Bulk Insert)
                placeholders = ','.join(['?'] * len(headers))
                data = [tuple(row[h] for h in reader.fieldnames) for row in reader]
                conn.executemany(f"INSERT INTO reporte_arl VALUES ({placeholders})", data)
                conn.commit()
                print(f"✅ Carga exitosa ({enc}). {len(data)} registros importados a SQLite.")
                break # Salir del bucle si funciona
        except (UnicodeDecodeError, csv.Error): continue
    
    # Exportar resultado
    cursor = conn.execute("SELECT * FROM reporte_arl")
    rows = cursor.fetchall()
    if rows:
        with open(CSV_OUT, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerows([list(map(lambda x: x[0], cursor.description))] + rows)
        print(f"✅ Exportación finalizada: {CSV_OUT}")
    conn.close()

if __name__ == '__main__': procesar_etl()