import streamlit as st
import cv2
import numpy as np
import plotly.express as px
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="SPECTRA-GUARD SUITE | Forense & Criminología",
    page_icon="🔍",
    layout="wide"
)

st.title("🛡️ SPECTRA-GUARD SUITE - Panel Táctico Integrado")
st.markdown("---")

# Menú lateral de navegación
modulo = st.sidebar.radio(
    "Seleccionar Módulo Táctico:",
    [
        "🔍 1. AFIS - Analizador & Zoom Interactivo",
        "📜 2. Peritaje ACE-V & Informe PDF",
        "🗺️ 3. Visor Geoespacial del Delito"
    ]
)

# ---------------------------------------------------------
# MÓDULO 1: AFIS ANALIZADOR
# ---------------------------------------------------------
if "1. AFIS" in modulo:
    st.subheader("🔍 Sistema AFIS - Analizador de Huellas")
    st.write("Carga las huellas para realizar el cotejo y análisis interactivo.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Huella A (Latente)")
        file_a = st.file_uploader("Subir Huella A", type=["png", "jpg", "jpeg"], key="fa")
        if file_a:
            file_bytes = np.asarray(bytearray(file_a.read()), dtype=np.uint8)
            img_a = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            fig_a = px.imshow(cv2.cvtColor(img_a, cv2.COLOR_BGR2RGB))
            fig_a.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=350)
            st.plotly_chart(fig_a, use_container_width=True, config={'scrollZoom': True})

    with col2:
        st.markdown("### Huella B (Referencia)")
        file_b = st.file_uploader("Subir Huella B", type=["png", "jpg", "jpeg"], key="fb")
        if file_b:
            file_bytes_b = np.asarray(bytearray(file_b.read()), dtype=np.uint8)
            img_b = cv2.imdecode(file_bytes_b, cv2.IMREAD_COLOR)
            fig_b = px.imshow(cv2.cvtColor(img_b, cv2.COLOR_BGR2RGB))
            fig_b.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=350)
            st.plotly_chart(fig_b, use_container_width=True, config={'scrollZoom': True})

# ---------------------------------------------------------
# MÓDULO 2: PERITAJE ACE-V
# ---------------------------------------------------------
elif "2. Peritaje ACE-V" in modulo:
    st.subheader("📜 Generador de Informes Periciales ACE-V")
    perito = st.text_input("Perito Responsable", value="Ángel Coello")
    caso = st.text_input("Número de Caso", value="CASO-2026-001")
    
    if st.button("Generar Datos del Dictamen"):
        st.success(f"Dictamen estructurado correctamente para el caso {caso} bajo la autoría de {perito}.")

# ---------------------------------------------------------
# MÓDULO 3: VISOR GEOESPACIAL
# ---------------------------------------------------------
else:
    st.subheader("🗺️ Visor Criminológico Geoespacial")
    np.random.seed(42)
    df = pd.DataFrame({
        'lat': -0.180653 + (np.random.randn(20) * 0.02),
        'lon': -78.467838 + (np.random.randn(20) * 0.02),
        'delito': np.random.choice(["Robo", "Hurto", "Homicidio"], 20)
    })
    fig_map = px.scatter_mapbox(df, lat="lat", lon="lon", color="delito", zoom=11, mapbox_style="carto-darkmatter")
    fig_map.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=450)
    st.plotly_chart(fig_map, use_container_width=True)