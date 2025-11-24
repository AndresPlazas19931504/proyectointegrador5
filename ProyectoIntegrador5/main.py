#Importamos las librerias requeridad

import sqlite3, csv, os

# Rutas críticas para la persistencia y la salida de datos.
# El uso de 'db/' implica una estructura de directorios modular.

DB_PATH, CSV_OUT = 'db/proyecto.db', 'db/export.csv'

# Directorios necesarios para el proyecto (BD y datos de entrada).
# El nombre del archivo de entrada es estático y denota la fuente de datos.

DIRS, FILENAME = ['db', 'data'], 'Estadisticas_Riegos_Laborales_Positiva-Sep_2025.csv'

# Creación idempotente de directorios (Idempotence via list comprehension).
# Asegura que las rutas 'db' y 'data' existan antes de cualquier I/O.

[os.makedirs(d, exist_ok=True) for d in DIRS]

# Lógica robusta para la detección de archivos de entrada.
# Intenta buscar el archivo en 'data/' y en el directorio raíz.
# Utiliza una expresión generadora `next()` para encontrar la primera ruta válida,
# o por defecto usa la ruta esperada en 'data/' (aunque no exista, la función de dummy la creará).

file_path = next((p for p in [os.path.join('data', FILENAME), FILENAME] if os.path.exists(p)), os.path.join('data', FILENAME))

# --- Funciones de Utilidad ---

def generar_dummy_si_no_existe():
    """
    Genera datos de prueba (dummy data) si el archivo de entrada esperado no se encuentra.
    Esto es crucial para asegurar la ejecutabilidad y la prueba unitaria del script ETL
    en entornos donde la fuente de datos aún no está disponible (ej. desarrollo inicial).
    """
    if not os.path.exists(file_path):
        print("Archivo no encontrado. Generando datos de prueba para testing...")
        
        # Definición simplificada de la estructura de datos para el prototipo.

        cols = ['ACTIVEC', 'AÑO', 'ARL', 'DPTO', 'INC_AT', 'INC_EL', 'MES', 'MPIO', 'MUERTES', 'PEN_AT', 'PEN_EL', 'PRESUNTOS', 'DEP', 'INDEP']
        
        # Uso de `newline=''` para evitar problemas de doble espaciado en Windows,
        # y `encoding='utf-8'` como estándar para manejo de caracteres especiales.

        with open(file_path, 'w', newline='', encoding='utf-8') as f:

            # Escribe la cabecera y una fila de datos simulados.

            csv.writer(f).writerows([cols, ['Construcción', '2023', 'ARL-1', 'Bogota', 0, 0, 'Enero', 'Bogota', 0, 0, 0, 10, 100, 20]])

def procesar_etl():

    """
    Ejecuta el pipeline de Extracción, Transformación y Carga (ETL) principal.
    
    1. E: Extrae datos del CSV.
    2. T: Realiza una transformación mínima (limpieza de encabezados, inferencia de tipos).
    3. L: Carga los datos en una base de datos SQLite (in-memory, ideal para prototipos).
    """
    generar_dummy_si_no_existe()

    conn = sqlite3.connect(DB_PATH) # Conexión al motor de base de datos.
    
    # --- Extracción (E) y Transformación (T) ---
    
    # Lógica de "prueba y error" para el manejo de codificaciones.
    # Aborda el problema común de los archivos CSV que no son estrictamente UTF-8.

    for enc in ['utf-8', 'latin-1', 'cp1252']:

        try:

            with open(file_path, encoding=enc) as f:
                # Detección dinámica del dialecto CSV (separador, comillas).
                # Se lee un fragmento inicial para inferir el formato.

                dialect = csv.Sniffer().sniff(f.read(1024)); f.seek(0)
                reader = csv.DictReader(f, dialect=dialect)
                
                # Pre-procesamiento de encabezados: estandarización/limpieza de espacios.

                headers = [h.strip() for h in reader.fieldnames]
                
                # --- Carga (L) a SQLite ---
                
                # *** 1. Estrategia de Carga: TRUNCATE & LOAD (Reinicialización) ***
                # Se elimina la tabla si existe y se recrea para un ciclo de carga limpio.

                conn.execute("DROP TABLE IF EXISTS reporte_arl")
                
                # Generación dinámica del DDL (Data Definition Language) para la tabla.
                # Nota: Se usa TEXT para todos los campos, simplificando la inferencia de tipos,
                # lo cual es común en la etapa de 'staging' de un ETL. Los espacios se reemplazan.

                column_defs = ', '.join(h.replace(' ', '_') + ' TEXT' for h in headers)
                conn.execute(f"CREATE TABLE reporte_arl ({column_defs})")
                
                # Preparación para Inserción Masiva (Bulk Insert) para optimizar el rendimiento.
                # Se mapean los datos del lector a una lista de tuplas.

                placeholders = ','.join(['?'] * len(headers))
                data = [tuple(row[h] for h in reader.fieldnames) for row in reader]
                
                # `executemany` es más eficiente que múltiples `execute`.

                conn.executemany(f"INSERT INTO reporte_arl VALUES ({placeholders})", data)
                conn.commit() # Transacción: Persiste los cambios a disco.
                
                print(f"Carga exitosa (Encoding: {enc}). {len(data)} registros importados a SQLite.")
                break # Éxito: Salir del bucle de codificación.
                
        # Manejo de excepciones específicas de I/O y formato CSV.

        except (UnicodeDecodeError, csv.Error): continue 
    
    # --- Exportación Final (Post-Procesamiento/Reporte) ---
    
    # Recuperación de todos los datos cargados para exportar (SELECT *).

    cursor = conn.execute("SELECT * FROM reporte_arl")
    rows = cursor.fetchall()
    
    if rows:

        # Recuperación de los nombres de columna correctos del objeto Cursor.

        column_names = list(map(lambda x: x[0], cursor.description))
        
        with open(CSV_OUT, 'w', newline='', encoding='utf-8') as f:

            # Escribe primero la cabecera, luego las filas de datos.

            csv.writer(f).writerows([column_names] + rows)
        print(f"Exportación finalizada: {CSV_OUT}")
        
    conn.close() # Cierre limpio de la conexión a la base de datos.

# --- Punto de Entrada del Script (Main Execution Block) ---

if __name__ == '__main__': 
    # Patrón de ejecución estándar para scripts modulares.
    procesar_etl()