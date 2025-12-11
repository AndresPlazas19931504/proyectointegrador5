# Importamos las librerías necesarias: sqlite3 para la base de datos, csv para manejar archivos CSV y os para operaciones del sistema operativo.
import sqlite3, csv, os

# Rutas para el archivo de la base de datos SQLite y el archivo CSV de salida.
DB_PATH, CSV_OUT = 'db/proyecto.db', 'db/export.csv'

# Directorios que deben existir (db para la base de datos, data para los archivos de entrada) y el nombre del archivo de datos de entrada.
DIRS, FILENAME = ['db', 'data'], 'Estadisticas_Riegos_Laborales_Positiva-Sep_2025.csv'

# Crea los directorios 'db' y 'data' si aún no existen.
[os.makedirs(d, exist_ok=True) for d in DIRS]

# Busca la ruta del archivo de entrada. Primero en 'data/' y luego en el directorio raíz.
# Si no lo encuentra, usa la ruta 'data/NOMBRE_ARCHIVO' por defecto.
file_path = next((p for p in [os.path.join('data', FILENAME), FILENAME] if os.path.exists(p)), os.path.join('data', FILENAME)

# --- Funciones Principales ---

def generar_dummy_si_no_existe():
    # Esta función crea un archivo CSV de prueba con datos mínimos si el archivo de entrada no se encuentra.
    if not os.path.exists(file_path):
        print("Archivo no encontrado. Generando datos de prueba para testing...")
        
        # Define los nombres de las columnas para el archivo de prueba.
        cols = ['ACTIVEC', 'AÑO', 'ARL', 'DPTO', 'INC_AT', 'INC_EL', 'MES', 'MPIO', 'MUERTES', 'PEN_AT', 'PEN_EL', 'PRESUNTOS', 'DEP', 'INDEP']
        
        # Abre el archivo para escribir los datos de prueba.
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            # Escribe la fila de encabezados y una fila de datos de ejemplo.
            csv.writer(f).writerows([cols, ['Construcción', '2023', 'ARL-1', 'Bogota', 0, 0, 'Enero', 'Bogota', 0, 0, 0, 10, 100, 20]])

def procesar_etl():
    # Función principal que realiza la Extracción (E), Transformación (T) y Carga (L) de datos (ETL).
    
    # 1. Asegura que el archivo exista o crea uno de prueba (si es necesario).
    generar_dummy_si_no_existe()

    # Conecta o crea la base de datos SQLite.
    conn = sqlite3.connect(DB_PATH) 
    
    # --- Extracción (E) y Transformación (T) ---
    
    # Intenta leer el archivo CSV con diferentes codificaciones (utf-8, latin-1, cp1252) para evitar errores.
    for enc in ['utf-8', 'latin-1', 'cp1252']:

        try:

            with open(file_path, encoding=enc) as f:
                # Lee un fragmento del archivo para detectar automáticamente el formato (separador, comillas, etc.).
                dialect = csv.Sniffer().sniff(f.read(1024)); f.seek(0)
                reader = csv.DictReader(f, dialect=dialect)
                
                # Prepara los nombres de las columnas, eliminando espacios al inicio y final.
                headers = [h.strip() for h in reader.fieldnames]
                
                # --- Carga (L) a SQLite ---
                
                # Elimina la tabla 'reporte_arl' si ya existe para empezar una carga limpia.
                conn.execute("DROP TABLE IF EXISTS reporte_arl")
                
                # Crea la sentencia SQL para crear la tabla usando los encabezados del CSV.
                # Todos los campos se definen como TEXTO y los espacios en los nombres se reemplazan por guiones bajos.
                column_defs = ', '.join(h.replace(' ', '_') + ' TEXT' for h in headers)
                conn.execute(f"CREATE TABLE reporte_arl ({column_defs})")
                
                # Prepara la sentencia INSERT (con '?') y extrae los datos del lector CSV.
                placeholders = ','.join(['?'] * len(headers))
                # Los datos se transforman en una lista de tuplas para la inserción masiva.
                data = [tuple(row[h] for h in reader.fieldnames) for row in reader]
                
                # Inserta todos los datos de golpe (executemany) para mayor eficiencia.
                conn.executemany(f"INSERT INTO reporte_arl VALUES ({placeholders})", data)
                conn.commit() # Guarda los cambios en la base de datos.
                
                print(f"Carga exitosa (Encoding: {enc}). {len(data)} registros importados a SQLite.")
                break # Si tiene éxito, sale del bucle de codificación.
                
        # Si la codificación falla o hay un error de formato CSV, intenta con la siguiente codificación.
        except (UnicodeDecodeError, csv.Error): continue 
    
    # --- Exportación Final (Reporte) ---
    
    # Consulta todos los datos cargados en la tabla.
    cursor = conn.execute("SELECT * FROM reporte_arl")
    rows = cursor.fetchall()
    
    if rows:
        # Obtiene los nombres de las columnas desde el cursor de la base de datos.
        column_names = list(map(lambda x: x[0], cursor.description))
        
        # Abre el archivo de salida CSV para escribir el reporte final.
        with open(CSV_OUT, 'w', newline='', encoding='utf-8') as f:
            # Escribe los nombres de las columnas y luego todas las filas de datos.
            csv.writer(f).writerows([column_names] + rows)
        print(f"Exportación finalizada: {CSV_OUT}")
        
    conn.close() # Cierra la conexión a la base de datos.

# --- Bloque de Ejecución ---

if __name__ == '__main__':  
    # Ejecuta la función principal cuando el script se corre directamente.
    procesar_etl()
