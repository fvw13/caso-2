import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Rappi AI Operations Hub", layout="wide", page_icon="🤖")

# --- 1. LÓGICA DE CARGA (Desde datos.xlsx) ---
@st.cache_data
def cargar_todo():
    try:
        # Nombre del archivo maestro
        archivo = 'datos.xlsx' 
        
        # Carga de pestañas (Sheet names deben coincidir con tu Excel)
        df_metrics = pd.read_excel(archivo, sheet_name='RAW_INPUT_METRICS')
        df_orders = pd.read_excel(archivo, sheet_name='RAW_ORDERS')
        
        # Limpieza de nombres de columnas (quitar espacios invisibles)
        df_metrics.columns = [c.strip() for c in df_metrics.columns]
        df_orders.columns = [c.strip() for c in df_orders.columns]

        # Identificar columnas de semanas (ej: L0W, L1W, L0W_ROLL)
        week_cols = [col for col in df_metrics.columns if 'W' in col]
        
        # Transformar métricas a formato largo (Tidy Data)
        df_long = df_metrics.melt(
            id_vars=['COUNTRY', 'CITY', 'ZONE', 'ZONE_TYPE', 'ZONE_PRIORITIZATION', 'METRIC'],
            value_vars=week_cols, 
            var_name='WEEK', 
            value_name='VALUE'
        )
        
        # Extraer número de semana de forma robusta
        df_long['WEEK_NUM'] = df_long['WEEK'].str.extract(r'(\d+)').astype(float)
        
        return df_long, df_orders
    except Exception as e:
        st.error(f"Error crítico al cargar 'datos.xlsx': {e}")
        return None, None

# Ejecutar carga
df_metrics, df_orders = cargar_todo()

# --- 2. MOTOR DE INSIGHTS (Zonas Críticas) ---
def generar_insights(df):
    hallazgos = []
    # Agrupamos por Zona y Métrica para comparar semanas
    for (zona, metrica), group in df.groupby(['ZONE', 'METRIC']):
        # Ordenamos: WEEK_NUM 0 (L0W) es la más reciente
        group = group.sort_values('WEEK_NUM', ascending=True) 
        vals = group['VALUE'].tolist()
        
        if len(vals) >= 2:
            actual = vals[0]  # Semana actual (L0W)
            previa = vals[1]  # Semana anterior (L1W)
            
            if previa != 0 and not pd.isna(actual) and not pd.isna(previa):
                cambio = (actual - previa) / abs(previa)
                hallazgos.append({
                    "Zona": zona, 
                    "Métrica": metrica, 
                    "Variación_Num": cambio, # Para ordenar internamente
                    "Variación": f"{cambio:.1%}",
                    "Valor Actual": round(actual, 2)
                })
    
    if not hallazgos:
        return pd.DataFrame()

    df_res = pd.DataFrame(hallazgos)
    
    # Filtramos variaciones significativas (>5%)
    criticos = df_res[df_res['Variación_Num'].abs() > 0.05]
    
    # Si no hay cambios > 5%, mostramos los 10 cambios más grandes que existan por defecto
    if criticos.empty:
        return df_res.sort_values('Variación_Num', key=abs, ascending=False).head(10).drop(columns=['Variación_Num'])
    
    return criticos.sort_values('Variación_Num', ascending=True).head(15).drop(columns=['Variación_Num'])

# --- 3. INTERFAZ DE USUARIO Y CHATBOT ---
st.title("🤖 Rappi AI Operations Bot")
st.markdown("---")

if df_metrics is not None:
    # Barra lateral de herramientas
    with st.sidebar:
        st.header("📊 Panel de Control")
        if st.button("🔍 Reporte de Anomalías"):
            st.subheader("Anomalías detectadas (L0W vs L1W)")
            res_manual = generar_insights(df_metrics)
            st.dataframe(res_manual)
        
        st.info("Este bot analiza variaciones semanales y tendencias de crecimiento en tiempo real.")

    # Inicializar historial de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar historial de mensajes
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada del Chat
    if prompt := st.chat_input("Escribe tu duda operativa aquí..."):
        # Agregar mensaje del usuario al historial
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Lógica de respuesta del asistente
        with st.chat_message("assistant"):
            query = prompt.lower()
            
            # CASO A: Zonas Críticas
            if any(x in query for x in ["crítica", "problema", "anomalía", "mal", "fallando"]):
                res = generar_insights(df_metrics)
                if not res.empty:
                    respuesta = "He identificado las siguientes zonas con variaciones significativas en la última semana:"
                    st.markdown(respuesta)
                    st.table(res.head(10))
                else:
                    respuesta = "No se detectaron anomalías mayores al 5%. La operación se mantiene estable."
                    st.markdown(respuesta)
            
            # CASO B: Órdenes y Tendencias
            elif any(x in query for x in ["orden", "crecimiento", "tendencia", "evolución"]):
                respuesta = "Analizando la tendencia de órdenes de las zonas con mayor volumen (L8W a L0W):"
                st.markdown(respuesta)
                # Buscamos columnas que representen semanas en df_orders
                cols_w = [c for c in df_orders.columns if 'W' in c]
                chart_data = df_orders.set_index('ZONE')[cols_w].T
                st.line_chart(chart_data.iloc[:, :5]) # Graficar top 5 zonas
            
            # CASO C: Comparar Wealthy vs Non-Wealthy
            elif any(x in query for x in ["comparar", "tipo", "wealthy", "segmento"]):
                respuesta = "Comparativa de desempeño promedio actual por Tipo de Zona (ZONE_TYPE):"
                st.markdown(respuesta)
                # Tomamos la semana más reciente (mínimo WEEK_NUM)
                ultima_sem = df_metrics[df_metrics['WEEK_NUM'] == df_metrics['WEEK_NUM'].min()]
                comp = ultima_sem.groupby('ZONE_TYPE')['VALUE'].mean()
                st.bar_chart(comp)
            
            # CASO D: Ayuda / Default
            else:
                respuesta = """Puedo ayudarte con tres tipos de análisis:
1. **Zonas Críticas**: Pregunta por *"problemas"* o *"anomalías"*.
2. **Tendencias**: Pregunta por *"órdenes"* o *"crecimiento"*.
3. **Comparativas**: Pregunta por *"comparar tipos de zona"*. """
                st.markdown(respuesta)
            
            # Guardar respuesta en el historial
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
else:
    st.error("Error: No se pudo inicializar la aplicación. Verifica que 'datos.xlsx' esté en la carpeta raíz.")