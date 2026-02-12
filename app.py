import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import os

st.set_page_config(page_title="Dashboard Anglo", layout="wide")

# --- FUNCIÓN DE CARGA AUTOMÁTICA DESDE GITHUB ---
def cargar_datos(palabra_clave):
    # Busca en la carpeta del servidor
    archivos = glob.glob(f"*{palabra_clave}*.xlsx")
    if not archivos: return pd.DataFrame(), False
    
    # Toma el más nuevo
    archivo_mas_nuevo = max(archivos, key=os.path.getctime)
    try:
        return pd.read_excel(archivo_mas_nuevo, engine='openpyxl'), True
    except:
        return pd.DataFrame(), False

# --- CARGA ---
df_docs, hay_docs = cargar_datos("Docs")
df_flujo, hay_flujo = cargar_datos("Flujo")
df_hist, hay_hist = cargar_datos("Historial")

if not hay_docs:
    st.error("⚠️ Sincronizando datos... Espera unos segundos o sube el reporte 'Docs' a la carpeta.")
    st.stop()

# --- PROCESAMIENTO ---
if 'Contrato' in df_docs.columns:
    df_docs['Contrato_Corto'] = df_docs['Contrato'].astype(str).str.split('-').str[0]
else:
    df_docs['Contrato_Corto'] = "General"

# --- DASHBOARD ---
st.title(f"🏗️ Dashboard Anglo - {len(df_docs)} Documentos")
st.markdown("Datos sincronizados automáticamente del servidor.")

# Filtros y Pestañas (Tu lógica estándar)
lista = sorted(df_docs['Contrato_Corto'].unique().tolist())
lista.insert(0, "Todos")
sel = st.sidebar.selectbox("Contrato:", lista)

df_view = df_docs[df_docs['Contrato_Corto'] == sel] if sel != "Todos" else df_docs

c1, c2, c3 = st.columns(3)
c1.metric("Total", len(df_view))
aprobados = len(df_view[df_view['Estatus'].astype(str).str.contains('Aprobado|Proceed', case=False)])
c2.metric("✅ Aprobados", aprobados)

st.dataframe(df_view, use_container_width=True)
