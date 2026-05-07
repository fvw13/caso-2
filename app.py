import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Rappi AI Ops Bot", layout="wide")

@st.cache_data
def cargar_todo():
    try:
        archivo = 'datos.xlsx' 
        df_metrics = pd.read_excel(archivo, sheet_name='RAW_INPUT_METRICS')
        df_orders = pd.read_excel(archivo, sheet_name='RAW_ORDERS')
        
        # LIMPIEZA EXTREMA
        for df in [df_metrics, df_orders]:
            df.columns = [str(c).strip().upper() for c in df.columns]
            # Limpiar espacios en celdas de texto
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str).str.strip()

        # Identificar columnas de semanas (L0W_ROLL, L1W_ROLL...)
        week_cols = [col for col in df_metrics.columns if 'W_ROLL' in col]
        
        df_long = df_metrics.melt(
            id_vars=['COUNTRY', 'CITY', 'ZONE', 'ZONE_TYPE', 'METRIC'],
            value_vars=week_cols, var_name='WEEK', value_name='VALUE'
        )
        # Extraer número de semana: "L0W_ROLL" -> 0
        df_long['WEEK_NUM'] = df_long['WEEK'].str.extract(r'(\d+)').astype(float)
        
        return df_long, df_orders
    except Exception as e:
        st.error(f"Error cargando Excel: {e}")
        return None, None

df_metrics, df_orders = cargar_todo()

# --- MOTOR DE FILTRADO ROBUSTO ---
def filtrar_datos(df, prompt):
    # Palabras a ignorar para no confundir al filtro
    ignore = ["EN", "LAS", "LOS", "DE", "ZONAS", "CRITICAS", "MOSTRAR", "DAME"]
    palabras_usuario = [p for p in prompt.upper().split() if p not in ignore]
    
    df_f = df.copy()
    filtros_aplicados = []

    # 1. Buscar País
    paises_disponibles = df['COUNTRY'].unique()
    for p in paises_disponibles:
        if p in palabras_usuario:
            df_f = df_f[df_f['COUNTRY'] == p]
            filtros_aplicados.append(f"País: {p}")
            break

    # 2. Buscar Ciudad (Coincidencia parcial)
    ciudades = df['CITY'].unique()
    for c in ciudades:
        if c.upper() in " ".join(palabras_usuario):
            df_f = df_f[df_f['CITY'] == c]
            filtros_aplicados.append(f"Ciudad: {c}")

    # 3. Buscar Tipo de Zona
    if "WEALTHY" in prompt.upper():
        tipo = "Wealthy" if "NON" not in prompt.upper() else "Non Wealthy"
        df_f = df_f[df_f['ZONE_TYPE'] == tipo]
        filtros_aplicados.append(f"Tipo: {tipo}")

    return df_f, filtros_aplicados

# --- INTERFAZ ---
st.title("🤖 Rappi AI Operations Bot")

if df_metrics is not None:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Ej: zonas criticas en MX o tendencias Quito"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            # Aplicar el nuevo motor de filtrado
            df_f, aplicados = filtrar_datos(df_metrics, prompt)
            
            if aplicados:
                st.success(f"✅ Filtros activos: {', '.join(aplicados)} | {len(df_f)} registros.")
            else:
                st.warning("⚠️ No detecté filtros específicos (país/ciudad). Mostrando datos globales.")

            q = prompt.lower()

            # LÓGICA DE RESPUESTA
            if any(x in q for x in ["critica", "problema", "anomalia"]):
                # Solo semana actual (0) y valores bajos
                criticas = df_f[(df_f['WEEK_NUM'] == 0) & (df_f['VALUE'] < 0.7)]
                if not criticas.empty:
                    st.dataframe(criticas[['COUNTRY', 'CITY', 'ZONE', 'METRIC', 'VALUE']].head(20))
                    msg = "Aquí tienes las zonas con métricas fuera de objetivo."
                else:
                    msg = "No encontré anomalías críticas con esos filtros."
            
            elif "comparar" in q:
                if not df_f.empty:
                    res = df_f[df_f['WEEK_NUM'] == 0].groupby('ZONE_TYPE')['VALUE'].mean()
                    st.bar_chart(res)
                    msg = "Comparativa generada."
                else:
                    msg = "Sin datos para comparar."

            elif "tendencia" in q:
                # Ver tendencia de las 5 zonas con más variación
                pivot = df_f.pivot_table(index='WEEK_NUM', columns='ZONE', values='VALUE', aggfunc='mean')
                st.line_chart(pivot.iloc[:, :5])
                msg = "Mostrando tendencias históricas."

            else:
                msg = "Puedo analizar 'zonas criticas', 'tendencias' o 'comparar' segmentos. Intenta incluir un país (MX, BR, EC)."

            st.write(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})
