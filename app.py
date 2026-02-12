import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Dashboard Control Documental", layout="wide")

# --- FUNCIÓN PARA CARGAR DATOS (CSV O EXCEL) ---
def cargar_datos(palabra_clave):
    # Busca archivos que coincidan con la palabra clave
    # Puede ser .csv o .xlsx
    archivos = glob.glob(f"*{palabra_clave}*")
    
    # Filtramos para que no tome el script .py ni archivos temporales
    archivos = [f for f in archivos if f.endswith(('.csv', '.xlsx')) and not f.startswith('~$')]
    
    if not archivos:
        return None, False
    
    # Toma el más reciente
    archivo_mas_nuevo = max(archivos, key=os.path.getctime)
    
    try:
        if archivo_mas_nuevo.endswith('.csv'):
            df = pd.read_csv(archivo_mas_nuevo)
        else:
            df = pd.read_excel(archivo_mas_nuevo, engine='openpyxl')
        return df, True
    except Exception as e:
        return None, False

# --- TÍTULO ---
st.title("🏗️ Dashboard de Control - Anglo American")

# --- CARGA DE REPORTES ---
# Aquí usamos los nombres clave que definimos
df_docs, hay_docs = cargar_datos("Docs")       # Reporte 1: General
df_flujo, hay_flujo = cargar_datos("Flujo")    # Reporte 2: Pendientes
df_hist, hay_hist = cargar_datos("Historial")  # Reporte 3: Análisis

if not hay_docs:
    st.warning("⚠️ Esperando archivo principal... Sube el reporte que contenga 'Docs' en el nombre.")
    st.stop()

# --- PROCESAMIENTO ---
# Extraer Contrato Corto
if 'Contrato' in df_docs.columns:
    df_docs['Contrato_Corto'] = df_docs['Contrato'].astype(str).str.split('-').str[0]
else:
    df_docs['Contrato_Corto'] = "General"

# --- SIDEBAR ---
st.sidebar.header("Filtros")
lista_contratos = sorted(df_docs['Contrato_Corto'].unique().tolist())
lista_contratos.insert(0, "Todos")
contrato_sel = st.sidebar.selectbox("Seleccionar Contrato:", lista_contratos)

# Función de filtro
def filtrar(df):
    if df is None or df.empty: return df
    if contrato_sel == "Todos": return df
    # Busca columnas que parezcan contrato
    cols = [c for c in df.columns if 'contrato' in c.lower()]
    if cols:
        return df[df[cols[0]].astype(str).str.contains(contrato_sel, na=False)]
    return df

# Aplicar filtros
df_docs_v = filtrar(df_docs)
df_flujo_v = filtrar(df_flujo)
df_hist_v = filtrar(df_hist)

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["📊 1. General (Docs)", "⏳ 2. Pendientes (Flujo)", "📈 3. Historial"])

# TAB 1: GENERAL
with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Documentos", len(df_docs_v))
    
    # Lógica de Estatus simplificada
    def get_status(x):
        s = str(x).lower()
        if 'aprobado' in s or 'proceed' in s: return 'Aprobado'
        if 'rechazado' in s or 'no proceder' in s: return 'Rechazado'
        return 'En Proceso'
    
    df_docs_v['Status_Simple'] = df_docs_v['Estatus'].apply(get_status)
    col2.metric("✅ Aprobados", len(df_docs_v[df_docs_v['Status_Simple']=='Aprobado']))
    col3.metric("❌ Rechazados", len(df_docs_v[df_docs_v['Status_Simple']=='Rechazado']))
    
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Distribución por Estatus")
        fig = px.pie(df_docs_v, names='Estatus', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Detalle")
        st.dataframe(df_docs_v[['No. de documento', 'Título', 'Estatus', 'Revisión']], use_container_width=True)

# TAB 2: FLUJO
with tab2:
    if not hay_flujo:
        st.info("ℹ️ Sube un archivo con nombre 'Flujo' para ver los pendientes.")
    else:
        st.header("Control de Pendientes")
        st.dataframe(df_flujo_v, use_container_width=True)

# TAB 3: HISTORIAL
with tab3:
    if not hay_hist:
        st.info("ℹ️ Sube un archivo con nombre 'Historial' para ver análisis.")
    else:
        st.header("Análisis Histórico")
        st.dataframe(df_hist_v, use_container_width=True)
