1. Descripción del Proyecto: Este proyecto implementa un flujo automatizado de Extracción, Transformación y Carga (ETL) para consolidar datos de riesgos laborales en Colombia. El objetivo es migrar un archivo plano (CSV) a una base de datos relacional local (SQLite) para asegurar la persistencia y facilitar el análisis posterior de indicadores clave como la accidentalidad, fatalidad y cobertura por actividad económica. La ejecución del script principal genera una base de datos estructurada que sirve como Repositorio de Datos Local para la analítica.

2. Tecnologías y Herramientas

- Python 3.x: Lenguaje principal para el script ETL.
- SQLite: Base de datos relacional local (no requiere instalación de servidor).
- Módulos de Python: sqlite3, csv, os.

3. Estructura de Carpetas


    ProyectoIntegrador5/
    ├── data/
    │   └── Estadisticas_Riegos_Laborales_Positiva-Sep-2025.csv  <- Archivo fuente original
    ├── db/
    │   ├── proyecto.db                                          <- Base de datos SQLite generada
    │   └── export.csv                                           <- Exportación final de la data limpia
    ├── docs/
    │   ├── Planificacion_Proyecto.xlsx                          <- Cronograma y planificación
    │   ├── Proyecto Integrado (EA1). Formulación de una necesidad de ingenieria de datos.docx <- Informe Formal
    │   └── Proyecto Integrado (EA1). Formulación de una necesidad de ingenieria de datos.pdf  <- Informe Formal (Entrega)
    ├── main.py                                                  <- Script principal (Lógica ETL)
    ├── ProyectoIntegrador5.pod                                  <- Archivo de configuración/dependencias del proyecto
    └── README.md


4. Instrucciones de Uso y Ejecución: Sigue estos pasos para replicar el proceso ETL en tu entorno local:

4.1. Requisitos Previos

- Asegúrate de tener Python 3.x instalado.
- Coloca el archivo Estadisticas_Riegos_Laborales_Positiva-Sep-2025.csv dentro de la carpeta /data.

4.2. Ejecución del Script

- Abre la terminal o línea de comandos (cmd/bash/Powershell).
- Navega hasta la carpeta raíz del proyecto (ProyectoIntegrador5).
- Ejecuta el script principal de Python:
        
        python main.py


4.3. Resultado Esperado: Al finalizar la ejecución, el script:

- Crea la carpeta /db (si no existe).
- Crea/actualiza la base de datos db/proyecto.db.
- Exporta el resultado estructurado a db/export.csv.

5. Documentación y Entrega: Este repositorio contiene los artefactos de desarrollo requeridos. Los documentos formales de planificación y análisis se encuentran en la carpeta docs/ y deben ser consultados en la plataforma LMS.

- Planificación: docs/Planificacion_Proyecto.xlsx.
- Informe Formal: El archivo docs/Proyecto Integrado.