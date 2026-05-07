import pandas as pd

def cargar_y_limpiar_datos():
    # Nombre del archivo único
    archivo = 'datos.xlsx'
    
    # 1. Cargar las pestañas específicas del Excel
    # El parámetro sheet_name debe coincidir con el nombre de la pestaña en tu Excel
    df_metrics = pd.read_excel(archivo, sheet_name='RAW_INPUT_METRICS')
    df_orders = pd.read_excel(archivo, sheet_name='RAW_ORDERS')
    
    # 2. Identificar columnas de semanas (L0W_ROLL, L1W, etc.)
    # Usamos una lógica más flexible por si los nombres varían un poco
    week_cols = [col for col in df_metrics.columns if 'W' in col]
    
    # 3. Transformar a formato largo (Tidy Data)
    df_metrics_long = df_metrics.melt(
        id_vars=['COUNTRY', 'CITY', 'ZONE', 'ZONE_TYPE', 'ZONE_PRIORITIZATION', 'METRIC'],
        value_vars=week_cols,
        var_name='WEEK',
        value_name='VALUE'
    )
    
    # 4. Convertir WEEK a numérico (extrae el número de L0W, L1W, etc.)
    # El prefijo 'r' evita el SyntaxWarning que tenías antes
    df_metrics_long['WEEK_NUM'] = df_metrics_long['WEEK'].str.extract(r'(\d+)').astype(int)
    
    return df_metrics_long, df_orders