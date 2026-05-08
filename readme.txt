para correrlo en VS

$env:PYTHONPATH = "."; & C:\Users\ASUS\AppData\Local\Python\pythoncore-3.14-64\python.exe -m streamlit run app.py


Este repositorio contiene un ecosistema de herramientas en Python diseñado para la automatización de operaciones y el análisis de inteligencia competitiva en Rappi. El sistema permite transformar datos crudos de métricas operacionales en insights accionables mediante un motor de detección de anomalías y una interfaz conversacional inteligente.

📁 Estructura del Proyecto
El ecosistema se divide en tres componentes modulares:

carga_datos.py (Data Pipeline): Módulo encargado del ETL. Transforma archivos Excel multietiqueta en un formato Tidy Data (long format), normalizando las series temporales de semanas (L0W, L1W, etc.) para análisis estadístico.

motor.py (Analytics Engine): El "cerebro" del sistema. Implementa lógica de detección de:

Anomalías: Cambios bruscos (>10%) en la última semana.

Tendencias Preocupantes: Identificación de degradación continua de métricas durante 4 semanas consecutivas.

app.py (Intelligence Interface): Dashboard interactivo construido en Streamlit. Utiliza un motor de procesamiento de lenguaje natural (NLP) simplificado para filtrar datos por país, ciudad y segmento socioeconómico mediante prompts del usuario.

🛠️ Stack Tecnológico
Core: Python 3.12+

Data Manipulation: Pandas & NumPy

Frontend / UX: Streamlit

Data Source: Excel (Engine: openpyxl)

🚀 Funcionalidades Clave
1. Motor de Filtrado Semántico
La aplicación permite interactuar con los datos de forma natural. Puedes realizar consultas como:

"Zonas críticas en MX"

"Tendencias en Bogotá"

"Comparar segmentos Wealthy vs Non-Wealthy"

2. Detección Automática de Deterioros
El sistema identifica automáticamente si una zona (ej. Ciudad de México o Quito) presenta una caída en métricas clave de servicio o demanda, priorizando aquellas que están por debajo del 70% de cumplimiento del objetivo.

3. Visualización Dinámica
Generación automática de:

Gráficos de Líneas: Para el seguimiento de tendencias históricas.

Gráficos de Barras: Para benchmarking entre tipos de zonas (Wealthy vs. Non-Wealthy).

Tablas de Scoring: Listado priorizado de zonas que requieren intervención inmediata.
