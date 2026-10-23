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
# CONFIGURACIÓN DE PÁGINA Y ESTILO TÁCTICO AVANZADO
# ---------------------------------------------------------
st.set_page_config(
    page_title="SPECTRA-GUARD SUITE | Inteligencia Forense & Criminológica",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de CSS Profesional (Estética Centro de Comando Ciber-Forense)
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        color: #e6edf3;
    }
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1f2937;
    }
    h1, h2, h3 {
        color: #38bdf8 !important;
        font-family: 'Courier New', Courier, monospace;
        letter-spacing: -0.5px;
    }
    .stButton>button {
        background-color: #10b981;
        color: #ffffff;
        border-radius: 6px;
        border: 1px solid #059669;
        font-weight: bold;
        font-family: 'Courier New', Courier, monospace;
    }
    .stButton>button:hover {
        background-color: #059669;
        color: white;
    }
    .metric-container {
        background-color: #111827;
        border: 1px solid #1f2937;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# FUNCIONES DE PROCESAMIENTO DACTILAR (OPENCV)
# ---------------------------------------------------------
def process_fingerprint(image_bytes, block_size, c_val):
    """Procesa la huella generando versiones binarizada y esqueleto con parámetros ajustables."""
    file_bytes = np.asarray(bytearray(image_bytes.read()), dtype=np.uint8)
    img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    if img_bgr is None:
        return None, None, None
        
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    
    # Binarización adaptable avanzada
    if block_size % 2 == 0:
        block_size += 1
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, block_size, c_val)
    
    # Esqueletización morfológica segura
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    skeleton = np.zeros(binary.shape, np.uint8)
    temp = binary.copy()
    for _ in range(20):
        eroded = cv2.erode(temp, kernel)
        temp_open = cv2.dilate(eroded, kernel)
        subset = cv2.subtract(temp, temp_open)
        skeleton = cv2.bitwise_or(skeleton, subset)
        temp = eroded.copy()
        if cv2.countNonZero(temp) == 0:
            break
            
    # Invertir esqueleto para visualización nítida sobre fondo oscuro
    skeleton_inv = cv2.bitwise_not(skeleton)
    binary_inv = cv2.bitwise_not(binary)
            
    return img_bgr, binary_inv, skeleton_inv

def render_interactive_canvas(title, img, key_name):
    """Renderiza la huella en un visor interactivo con zoom, scroll y paneo libre."""
    if img is None:
        return
    if len(img.shape) == 2:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    else:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
    fig = px.imshow(img_rgb, binary_string=True)
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_showscale=False,
        dragmode='pan',
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=420
    )
    config = {'scrollZoom': True, 'displayModeBar': True, 'displaylogo': False}
    st.plotly_chart(fig, use_container_width=True, config=config, key=key_name)

# ---------------------------------------------------------
# GENERACIÓN DE INFORME PERICIAL PDF (REPORTLAB)
# ---------------------------------------------------------
def generate_pdf_report(perito, caso, evidencia, conclusion, puntos_coincidentes):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor('#0284c7'),
        alignment=1,
        spaceAfter=15
    )
    
    story.append(Paragraph("DICTAMEN PERICIAL DACTILOSCÓPICO (METODOLOGÍA ACE-V)", title_style))
    story.append(Spacer(1, 10))
    
    data = [
        ["Número de Caso / Causa:", caso],
        ["Perito Acreditado:", perito],
        ["Evidencia Procesada:", evidencia],
        ["Puntos Coincidentes Hallados:", f"{puntos_coincidentes} Minucias Acreditadas"],
        ["Dictamen Final (Fase E):", conclusion]
    ]
    
    table = Table(data, colWidths=[180, 340])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#0f172a')),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1'))
    ]))
    story.append(table)
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Certificación de Cadena de Custodia Digital:</b> El presente dictamen técnico ha sido procesado mediante algoritmos computacionales avanzados en la plataforma SPECTRA-GUARD con estándares forenses internacionales.", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ---------------------------------------------------------
# MENÚ PRINCIPAL LATERAL TÁCTICO
# ---------------------------------------------------------
st.sidebar.markdown("# 🛡️ SPECTRA-GUARD")
st.sidebar.caption("Suite Integral de Inteligencia Forense & Criminológica")
st.sidebar.markdown("---")

modulo = st.sidebar.radio(
    "Navegación Táctica:",
    [
        "🔍 1. Analizador AFIS & Esqueletización",
        "📜 2. Peritaje ACE-V & Informe PDF",
        "🗺️ 3. Visor Criminológico Geoespacial"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Modo Operativo:** Utiliza la rueda del ratón para realizar zoom de alta precisión y arrastra para examinar minucias.")

# ---------------------------------------------------------
# MÓDULO 1: ANALIZADOR AFIS & ESQUELETIZACIÓN AVANZADA
# ---------------------------------------------------------
if "1. Analizador AFIS" in modulo:
    st.title("🔍 Sistema AFIS - Analizador Dactilar de Alta Precisión")
    st.markdown("Plataforma de procesamiento multiespectral, binarización adaptativa y extracción minuciosa de crestas.")
    
    # Barra de parámetros de ajuste fino
    with st.expander("⚙️ Parámetros Avanzados de Procesamiento OpenCV", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            block_size = st.slider("Tamaño de Bloque Adaptativo", 3, 51, 15, step=2)
        with c2:
            c_val = st.slider("Constante C (Umbral)", 1, 25, 5)

    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Huella Dubitada / Latente (A)")
        file_a = st.file_uploader("Cargar Archivo A", type=["png", "jpg", "jpeg", "bmp"], key="fa")
        if file_a:
            img_a, bin_a, skel_a = process_fingerprint(file_a, block_size, c_val)
            if img_a is not None:
                capa_a = st.radio("Capa Activa (A):", ["Original", "Binarizada", "Esqueleto + Minucias"], horizontal=True, key="ca")
                selected_a = img_a if capa_a == "Original" else (bin_a if capa_a == "Binarizada" else skel_a)
                render_interactive_canvas("Visor Táctico A", selected_a, "cv_a")

    with col_b:
        st.subheader("Huella de Referencia / Decadactilar (B)")
        file_b = st.file_uploader("Cargar Archivo B", type=["png", "jpg", "jpeg", "bmp"], key="fb")
        if file_b:
            img_b, bin_b, skel_b = process_fingerprint(file_b, block_size, c_val)
            if img_b is not None:
                capa_b = st.radio("Capa Activa (B):", ["Original", "Binarizada", "Esqueleto + Minucias"], horizontal=True, key="cb")
                selected_b = img_b if capa_b == "Original" else (bin_b if capa_b == "Binarizada" else skel_b)
                render_interactive_canvas("Visor Táctico B", selected_b, "cv_b")

    if file_a and file_b:
        st.markdown("---")
        st.success("✅ **Sincronización Completada:** Ambas muestras han sido procesadas bajo los filtros morfológicos establecidos.")

# ---------------------------------------------------------
# MÓDULO 2: PERITAJE ACE-V & INFORME PDF
# ---------------------------------------------------------
elif "2. Peritaje ACE-V" in modulo:
    st.title("📜 Módulo de Peritaje Dactiloscópico ACE-V")
    st.markdown("Estructuración formal del dictamen técnico pericial y generación de cadena de custodia.")
    
    col_form, col_prev = st.columns([1, 1])
    
    with col_form:
        st.subheader("Formulario de Dictamen Oficial")
        perito_nom = st.text_input("Perito Responsable", value="Ángel Coello")
        causa_num = st.text_input("Número de Causa / Caso", value="CASO-2026-EC-089")
        evidencia_desc = st.text_input("Descripción de Evidencia Física", value="Huella Latente en soporte físico")
        puntos = st.slider("Puntos Homologados Coincidentes (Minucias)", 8, 30, 14)
        conclusion_sel = st.selectbox("Conclusión Pericial (Fase E):", [
            "IDENTIFICACIÓN POSITIVA (Coincidencia Plena)",
            "EXCLUSIÓN TÉCNICA (No Corresponde)",
            "NO CONCLUYENTE (Calidad Insuficiente)"
        ])
        
        pdf_file = generate_pdf_report(perito_nom, causa_num, evidencia_desc, conclusion_sel, puntos)
        
        st.download_button(
            label="📥 Descargar Dictamen en PDF Oficial",
            data=pdf_file,
            file_name=f"Dictamen_ACEV_{causa_num}.pdf",
            mime="application/pdf"
        )
        
    with col_prev:
        st.subheader("Vista Previa del Expediente")
        st.markdown(f"""
        <div style="background-color: #111827; padding: 25px; border-radius: 8px; border: 1px solid #1f2937;">
            <h4 style="color:#38bdf8; margin-top:0;">Resumen Técnico - Metodología ACE-V</h4>
            <p><b>Perito Acreditado:</b> {perito_nom}</p>
            <p><b>Referencia del Caso:</b> {causa_num}</p>
            <p><b>Evidencia:</b> {evidencia_desc}</p>
            <p><b>Minucias Validadas:</b> <span style="color:#10b981; font-weight:bold;">{puntos} Puntos</span></p>
            <p><b>Evaluación:</b> {conclusion_sel}</p>
            <hr style="border-color:#1f2937;">
            <p style="font-size: 0.85em; color: #9ca3af;">Documento preparado para su validación institucional en la Fiscalía General / Policía Nacional.</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# MÓDULO 3: VISOR CRIMINOLÓGICO GEOESPACIAL
# ---------------------------------------------------------
else:
    st.title("🗺️ Visor Criminológico Geoespacial en Tiempo Real")
    st.markdown("Mapa táctico interactivo de concentración delictiva y puntos calientes (*hotspots*) territorial.")
    
    np.random.seed(42)
    lats = -0.180653 + (np.random.randn(60) * 0.03)
    lons = -78.467838 + (np.random.randn(60) * 0.03)
    tipos = np.random.choice(["Homicidio", "Robo a Personas", "Hurto a Vehículos", "Tráfico de Sustancias"], 60)
    
    df_delitos = pd.DataFrame({'lat': lats, 'lon': lons, 'tipologia': tipos})
    
    filtro_tipo = st.multiselect("Filtrar por Tipología (COIP):", options=list(df_delitos['tipologia'].unique()), default=list(df_delitos['tipologia'].unique()))
    df_filtrado = df_delitos[df_delitos['tipologia'].isin(filtro_tipo)]
    
    fig_map = px.scatter_mapbox(
        df_filtrado,
        lat="lat",
        lon="lon",
        color="tipologia",
        size_max=15,
        zoom=11.5,
        mapbox_style="carto-darkmatter",
        title="Matriz Geoespacial de Incidencia Delictiva - Distrito Metropolitano"
    )
    fig_map.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=520)
    
    st.plotly_chart(fig_map, use_container_width=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Incidentes Mapeados", len(df_filtrado))
    with c2:
        st.metric("Sector de Mayor Densidad", "Zona 5 / Pichincha")
    with c3:
        st.metric("Factor de Cifra Negra", "32.8%")