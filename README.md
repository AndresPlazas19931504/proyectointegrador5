1. Descripción del Proyecto

Este proyecto implementa un flujo automatizado de Extracción, Transformación y Carga (ETL) para consolidar datos de riesgos laborales en Colombia. El objetivo inicial de migrar un archivo plano a una base de datos local (SQLite) evolucionó hacia una solución integral que realiza **limpieza avanzada, enriquecimiento temporal y Análisis Descriptivo (EDA)**, culminando con la construcción de un **Dashboard interactivo** para la visualización de indicadores clave (accidentalidad, fatalidad y cobertura por actividad económica).

2. Tecnologías y Herramientas

- **Python 3.x:** Lenguaje principal para ETL y análisis.
- **SQLite:** Base de datos relacional local para persistencia (Actividad 1).
- **Pandas:** Librería fundamental para la limpieza avanzada y el enriquecimiento de datos (Actividad 2).
- **Streamlit / Power BI / Tableau:** Herramienta de Visualización y Business Intelligence (Actividad 3).
- **Módulos Adicionales:** `sqlite3`, `csv`, `os`, `plotly` (para el dashboard), `matplotlib`, `seaborn` (para EDA).

3. Estructura de Carpetas

    ProyectoIntegrador5/
    ├── data/
    │   ├── Estadisticas_Riegos_Laborales_Positiva-Sep-2025.csv  <- Archivo fuente original
    │   └── dataset_enriquecido.csv                              <- Dataset limpio, enriquecido con fechas (Actividad 2)
    ├── db/
    │   ├── proyecto.db                                          <- Base de datos SQLite generada
    │   └── export.csv                                           <- Exportación final de la data limpia (Actividad 1)
    ├── docs/
    │   ├── Planificacion_Proyecto.xlsx                          <- Cronograma y planificación
    │   ├── Proyecto Integrado (EA1). Formulación de una necesidad de ingenieria de datos.docx <- Informe Formal (Actualizado)
    │   ├── Proyecto Integrado (EA1). Formulación de una necesidad de ingenieria de datos.pdf  <- Informe Formal (Entrega)
    │   ├── diagrama_gantt.png                                   <- Diagrama de Gantt final (Actividad 3)
    │   └── graficos/                                            <- Gráficos de EDA y visualizaciones finales (Actividad 2 y 3)
    ├── notebooks/                                               <- Notebooks de análisis y preparación
    │   └── 02_enriquecimiento_eda.ipynb                         <- Notebook de Limpieza, Enriquecimiento y EDA (Actividad 2)
    ├── dashboard/                                               <- Archivos de la aplicación de Business Intelligence (Actividad 3)
    │   └── app.py (o archivo .pbix/.twbx)                       <- Script principal del dashboard
    ├── main.py                                                  <- Script principal (Lógica ETL)
    └── README.md


4. Instrucciones de Uso y Ejecución

Sigue estos pasos para replicar el proceso completo y visualizar el dashboard:

4.1. Requisitos Previos

- Asegúrate de tener Python 3.x instalado.
- Instala las librerías necesarias: `pip install pandas streamlit plotly` (Ajustar según la herramienta BI).
- Coloca el archivo Estadisticas_Riegos_Laborales_Positiva-Sep-2025.csv dentro de la carpeta /data.

4.2. Ejecución del Script ETL (Actividad 1)

- Navega hasta la carpeta raíz del proyecto (`ProyectoIntegrador5`).
- Ejecuta el script principal de Python para generar la base de datos:
        
        python main.py

4.3. Preparación de Datos (Actividad 2)

- Ejecuta **completamente** el Notebook `notebooks/02_enriquecimiento_eda.ipynb`. Este paso es **obligatorio** para generar el archivo `data/dataset_enriquecido.csv` que alimenta el dashboard.

4.4. Ejecución del Dashboard (Actividad 3)

- Asegúrate de estar en la carpeta raíz del proyecto.
- Ejecuta la aplicación de Streamlit:

        streamlit run dashboard/app.py

4.5. Resultado Esperado

- Se genera la base de datos `db/proyecto.db` y el archivo `db/export.csv`.
- Se genera el archivo final `data/dataset_enriquecido.csv`.
- El dashboard interactivo se abre automáticamente en el navegador para el análisis de los riesgos laborales.

5. Documentación y Entrega

Este repositorio contiene los artefactos de desarrollo requeridos.

- La **Metodología completa**, el **Diagrama de Gantt** y los **Hallazgos Finales** se encuentran en el Documento de Proyecto actualizado (docs/Proyecto Integrado...).
- Los gráficos generados en la fase de EDA se encuentran en `docs/graficos/`.
