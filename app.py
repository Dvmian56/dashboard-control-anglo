import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import os

st.set_page_config(page_title="Dashboard Anglo", layout="wide")

# --- FUNCIÓN DE CARGA SIMPLE (SOLO EXCEL) ---
def cargar_excel(palabra_clave):
    # Busca archivos Excel con la palabra clave
    archivos = glob.glob(f"*{palabra_clave}*.xlsx")
    if not archivos: return pd.DataFrame(), False
    
    # Toma el más nuevo
    archivo_mas_nuevo = max(archivos, key=os.path.getctime)
    try:
        return pd.read_excel(archivo_mas_nuevo, engine='openpyxl'), True
    except Exception as e:
        return pd.DataFrame(), False

# --- CARGAMOS TUS 3 ARCHIVOS ---
df_docs, ok_docs = cargar_excel("Docs")      # El real de Aconex
df_flujo, ok_flujo = cargar_excel("Flujo")   # El que creamos
df_hist, ok_hist = cargar_excel("Historial") # El que creamos

if not ok_docs:
    st.error("⚠️ Error: No encuentro el Excel 'Docs'.")
    st.stop()

# --- PROCESAMIENTO ---
# Extraemos el contrato (CP...)
if 'Contrato' in df_docs.columns:
    df_docs['Contrato_Corto'] = df_docs['Contrato'].astype(str).str.split('-').str[0]
else:
    df_docs['Contrato_Corto'] = "General"

# --- INTERFAZ ---
st.title(f"🏗️ Dashboard Control Documental")

# Filtro de Contrato
lista = sorted(df_docs['Contrato_Corto'].unique().tolist())
lista.insert(0, "Todos")
sel = st.sidebar.selectbox("Seleccionar Contrato:", lista)

# Función de filtrado
def filtrar(df):
    if df.empty or sel == "Todos": return df
    # Busca columnas que contengan 'contrato'
    col = next((c for c in df.columns if 'contrato' in c.lower()), None)
    return df[df[col].astype(str).str.contains(sel, na=False)] if col else df

df_v = filtrar(df_docs)
df_f = filtrar(df_flujo)
df_h = filtrar(df_hist)

# --- PESTAÑAS ---
t1, t2, t3 = st.tabs(["📊 General", "🔥 Pendientes", "⏱️ Historial"])

with t1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Docs", len(df_v))
    aprobados = len(df_v[df_v['Estatus'].astype(str).str.contains('Aprobado|Proceed', case=False, na=False)])
    c2.metric("✅ Aprobados", aprobados)
    rechazados = len(df_v[df_v['Estatus'].astype(str).str.contains('Rechazado|No Proceder', case=False, na=False)])
    c3.metric("❌ Rechazados", rechazados)
    
    st.dataframe(df_v, use_container_width=True)

with t2:
    if not ok_flujo: st.warning("Falta archivo Flujo")
    else:
        vencidos = df_f[df_f['Días de Retraso'] > 0]
        st.metric("🔴 Documentos Vencidos", len(vencidos))
        st.dataframe(df_f, use_container_width=True)

with t3:
    if not ok_hist: st.warning("Falta archivo Historial")
    else:
        prom = df_h['Días Gestión'].mean()
        st.metric("Tiempo Promedio (Días)", f"{prom:.1f}")
        fig = px.histogram(df_h, x="Días Gestión", title="Distribución de Tiempos")
        st.plotly_chart(fig, use_container_width=True)
