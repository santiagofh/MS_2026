from pathlib import Path
import streamlit as st
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Dashboard Metas Sanitarias 2026",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --gob-red: #FE6565;
        --gob-blue: #006FB3;
        --gob-blue-soft: #EAF4FA;
    }

    .stApp h1, .stApp h2, .stApp h3 {
        color: var(--gob-blue);
        font-weight: 700;
    }

    .stApp [data-testid="stMetric"] {
        background: linear-gradient(180deg, #ffffff 0%, var(--gob-blue-soft) 100%);
        border: 1px solid #cfe6f4;
        border-radius: 12px;
        padding: 0.5rem 0.75rem;
    }

    .stApp button[kind="primary"] {
        background-color: var(--gob-red);
        border-color: var(--gob-red);
    }

    .stApp button[kind="secondary"] {
        border-color: var(--gob-blue);
        color: var(--gob-blue);
    }

    section[data-testid="stSidebar"] {
        border-right: 1px solid #cfe6f4;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.logo(
    str(BASE_DIR / "assets" / "seremi_sidebar_logo.svg"),
    size="large",
    icon_image=str(BASE_DIR / "assets" / "seremi_sidebar_icon.svg"),
)

def home():
    st.warning("Datos Provisorios")

    st.title('Bienvenidos al Dashboard de Metas Sanitarias 2026')

    st.subheader('Sistema integral para el seguimiento y control de las metas sanitarias')

    st.write("""
    Este dashboard está diseñado para proporcionar una visión completa y detallada de las metas sanitarias en las diversas áreas de salud pública.

    - Consultar el cumplimiento de las metas sanitarias por Servicio de salud, Comuna y Establecimiento de salud.
    - Ver gráficos y tablas detalladas que muestran el progreso y los indicadores de las metas sanitarias.
    """)
    st.write(f"## Datos para la Meta Sanitaria")

    st.write("Fecha de corte de datos:")
    fecha_corte = pd.read_csv("Fecha_corte_REM.csv")
    st.write(fecha_corte[['REM', 'Fecha_corte']].rename(columns={'Fecha_corte': 'Fecha Corte'}))
    st.write(""" comprometidos a proporcionar información precisa y actualizada para apoyar la toma de decisiones en el ámbito de la salud pública.""")

pages = {
    "Menu principal": [
        st.Page(home, default=True, title="Pagina de inicio", icon=":material/home:")
    ],
    "Metas Sanitarias": [
        st.Page("MSI.py", title="Meta I: Recuperación del Desarrollo Psicomotor", icon=":material/public:"),
        st.Page('MSII.py', title="Meta II: Detección precoz del cáncer de cuello uterino", icon=":material/public:"),
        st.Page('MSIIIa.py', title="Meta III.A: Control con Enfoque de Riesgo odontológico en población de 0 a 9 años", icon=":material/public:"),
        st.Page('MSIIIb.py', title="Meta III.B: Niños y niñas de 6 años libres de caries", icon=":material/public:"),
        st.Page('MSIVa.py', title="Meta IV.A: Cobertura efectiva de tratamiento de DM2 en personas de 15 y más años", icon=":material/public:"),
        st.Page('MSIVb.py', title="Meta IV.B: Evaluación anual del pie diabético en personas de 15 años y más", icon=":material/public:"),
        st.Page('MSV.py', title="Meta V: Cobertura de tratamiento en personas con HTA", icon=":material/public:"),
        st.Page('MSVI.py', title="Meta VI: Prevalencia de Lactancia Materna Exclusiva (LME) en menores de 6 meses de vida", icon=":material/public:"),
        st.Page('MSVII.py', title="Meta VII: Cobertura efectiva de tratamiento en enfermedades respiratorias crónicas (asma y EPOC) en personas de 5 años y más", icon=":material/public:")
    ]
}
pg = st.navigation(pages)
pg.run()
