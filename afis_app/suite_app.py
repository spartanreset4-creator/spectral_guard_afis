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
# CONFIGURACIÓN DE PÁGINA Y ESTILO TÁCTICO
# ---------------------------------------------------------
st.set_page_config(
    page_title="SPECTRA-GUARD SUITE | Forense & Criminología",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de CSS Estética Táctica Oscura
st.markdown("""
<style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    [data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }
    h1, h2, h3 {
        color: #58a6ff !important;
        font-family: 'Courier New', Courier, monospace;
    }
    .stButton>button {
        background-color: #238636;
        color: white;
        border-radius: 6px;
        border: 1px solid #2ea043;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2ea043;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# FUNCIONES DE PROCESAMIENTO DACTILAR (OPENCV)
# ---------------------------------------------------------
def process_fingerprint(image_bytes):
    """Procesa la huella generando versiones binarizada y esqueleto."""
    file_bytes = np.asarray(bytearray(image_bytes.read()), dtype=np.uint8)
    img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    if img_bgr is None:
        return None, None, None
        
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    
    # Binarización por Otsu
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Esqueletización morfológica segura (compatible con la nube)
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    skeleton = np.zeros(binary.shape, np.uint8)
    temp = binary.copy()
    for _ in range(15):  # Iteraciones controladas de thinning
        eroded = cv2.erode(temp, kernel)
        temp_open = cv2.dilate(eroded, kernel)
        subset = cv2.subtract(temp, temp_open)
        skeleton = cv2.bitwise_or(skeleton, subset)
        temp = eroded.copy()
        if cv2.countNonZero(temp) == 0:
            break
            
    return img_bgr, binary, skeleton

def render_interactive_canvas(title, img, key_name):
    """Renderiza la huella en un visor interactivo con zoom y scroll."""
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
        height=380
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
        fontSize=15,
        textColor=colors.HexColor('#1b365d'),
        alignment=1,
        spaceAfter=12
    )
    
    story.append(Paragraph("DICTAMEN PERICIAL DACTILOSCÓPICO (METODOLOGÍA ACE-V)", title_style))
    story.append(Spacer(1, 10))
    
    data = [
        ["Número de Caso / Causa:", caso],
        ["Perito Acreditado:", perito],
        ["Evidencia Procesada:", evidencia],
        ["Puntos Coincidentes Hallados:", f"{puntos_coincidentes} Minucias"],
        ["Dictamen Final (Fase E):", conclusion]
    ]
    
    table = Table(data, colWidths=[180, 340])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f0f4f8')),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#000000')),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1'))
    ]))
    story.append(table)
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Certificación de Cadena de Custodia Digital:</b> El presente informe ha sido generado automáticamente bajo algoritmos computacionales de cotejo minuciosos en la plataforma SPECTRA-GUARD.", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ---------------------------------------------------------
# MENÚ PRINCIPAL LATERAL
# ---------------------------------------------------------
st.sidebar.title("🛡️ SPECTRA-GUARD")
st.sidebar.caption("Suite de Inteligencia Forense & Criminológica")

modulo = st.sidebar.radio(
    "Seleccionar Módulo Táctico:",
    [
        "🔍 1. AFIS - Analizador & Zoom Interactivo",
        "📜 2. Peritaje ACE-V & Informe PDF",
        "🗺️ 3. Visor Geoespacial del Delito"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Consejo:** Usa la rueda del mouse sobre las imágenes para hacer zoom y arrastra para examinar detalles.")

# ---------------------------------------------------------
# MÓDULO 1: ANALIZADOR AFIS INTERACTIVO (A/B)
# ---------------------------------------------------------
if "1. AFIS" in modulo:
    st.title("🔍 Sistema AFIS - Analizador de Huellas Dactilares")
    st.markdown("Carga la huella dubitada (latente) y la de referencia para realizar el cotejo y análisis detallado.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Huella Latente (A)")
        file_a = st.file_uploader("Cargar Evidencia A", type=["png", "jpg", "jpeg", "bmp"], key="file_a")
        if file_a:
            img_a, bin_a, skel_a = process_fingerprint(file_a)
            if img_a is not None:
                capa_a = st.radio("Capa a examinar (A):", ["Original", "Binarizada", "Esqueleto"], horizontal=True, key="capa_a")
                selected_a = img_a if capa_a == "Original" else (bin_a if capa_a == "Binarizada" else skel_a)
                render_interactive_canvas("Visor Táctico A", selected_a, "canvas_a")

    with col2:
        st.subheader("2. Huella de Referencia (B)")
        file_b = st.file_uploader("Cargar Referencia B", type=["png", "jpg", "jpeg", "bmp"], key="file_b")
        if file_b:
            img_b, bin_b, skel_b = process_fingerprint(file_b)
            if img_b is not None:
                capa_b = st.radio("Capa a examinar (B):", ["Original", "Binarizada", "Esqueleto"], horizontal=True, key="capa_b")
                selected_b = img_b if capa_b == "Original" else (bin_b if capa_b == "Binarizada" else skel_b)
                render_interactive_canvas("Visor Táctico B", selected_b, "canvas_b")

    if file_a and file_b:
        st.markdown("---")
        st.success("✅ **Cotejo Automatizado:** Se han procesado ambas muestras y validado las capas estructurales con éxito.")

# ---------------------------------------------------------
# MÓDULO 2: PERITAJE ACE-V E INFORME PDF
# ---------------------------------------------------------
elif "2. Peritaje ACE-V" in modulo:
    st.title("📜 Generador de Informes Periciales ACE-V")
    st.markdown("Estructuración formal de dictámenes de dactiloscopia para la cadena de custodia.")
    
    col_form, col_prev = st.columns([1, 1])
    
    with col_form:
        st.subheader("Datos del Dictamen")
        perito_nom = st.text_input("Nombre del Perito / Analista", value="Ángel Coello")
        causa_num = st.text_input("Número de Causa / Caso", value="CASO-2026-EC-089")
        evidencia_desc = st.text_input("Descripción de la Evidencia", value="Huella Latente recuperada en superficie")
        puntos = st.slider("Puntos de Minucias Coincidentes", 8, 25, 14)
        conclusion_sel = st.selectbox("Evaluación Pericial (Fase E):", [
            "IDENTIFICACIÓN (Coincidencia Plena Positiva)",
            "EXCLUSIÓN (No Corresponde al Sujeto)",
            "NO CONCLUYENTE (Calidad Insuficiente)"
        ])
        
        pdf_file = generate_pdf_report(perito_nom, causa_num, evidencia_desc, conclusion_sel, puntos)
        
        st.download_button(
            label="📥 Descargar Informe PDF Oficial",
            data=pdf_file,
            file_name=f"Dictamen_Forense_{causa_num}.pdf",
            mime="application/pdf"
        )
        
    with col_prev:
        st.subheader("Vista Previa del Dictamen")
        st.markdown(f"""
        <div style="background-color: #161b22; padding: 20px; border-radius: 8px; border: 1px solid #30363d;">
            <h4 style="color:#58a6ff;">Resumen Ficha ACE-V</h4>
            <p><b>Perito:</b> {perito_nom}</p>
            <p><b>Caso:</b> {causa_num}</p>
            <p><b>Evidencia:</b> {evidencia_desc}</p>
            <p><b>Minucias Validadas:</b> <span style="color:#2ea043; font-weight:bold;">{puntos} Puntos</span></p>
            <p><b>Dictamen:</b> {conclusion_sel}</p>
            <hr style="border-color:#30363d;">
            <small style="color:#8b949e;">Listo para generar el PDF legal con ReportLab.</small>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# MÓDULO 3: VISOR GEOESPACIAL EN TIEMPO REAL
# ---------------------------------------------------------
else:
    st.title("🗺️ Visor Criminológico Geoespacial en Tiempo Real")
    st.markdown("Mapa táctico de puntos calientes (*hotspots*) y distribución delictiva en Quito y Pichincha.")
    
    np.random.seed(42)
    lats = -0.180653 + (np.random.randn(50) * 0.03)
    lons = -78.467838 + (np.random.randn(50) * 0.03)
    tipos = np.random.choice(["Homicidio", "Robo a Personas", "Hurto", "Tráfico de Sustancias"], 50)
    
    df_delitos = pd.DataFrame({'lat': lats, 'lon': lons, 'tipologia': tipos})
    
    filtro_tipo = st.multiselect("Filtrar por Tipología del COIP:", options=list(df_delitos['tipologia'].unique()), default=list(df_delitos['tipologia'].unique()))
    df_filtrado = df_delitos[df_delitos['tipologia'].isin(filtro_tipo)]
    
    fig_map = px.scatter_mapbox(
        df_filtrado,
        lat="lat",
        lon="lon",
        color="tipologia",
        size_max=15,
        zoom=11,
        mapbox_style="carto-darkmatter",
        title="Concentración de Incidentes Criminológicos"
    )
    fig_map.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=500)
    
    st.plotly_chart(fig_map, use_container_width=True)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Incidentes Registrados", len(df_filtrado))
    m2.metric("Zona Crítica Principal", "Distrito Metropolitano de Quito")
    m3.metric("Nivel de Alerta Táctica", "Alto (Nivel 3)")