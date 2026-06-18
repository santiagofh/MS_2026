import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

meta_tag = 'MSI'
meta_nacional = 0.9
meta_titulo = 'Meta I: Recuperaci\u00f3n del Desarrollo Psicomotor'

deis_path = "data/establecimientos_deis_actual.xlsx"

df_ms = pd.read_csv('MS2026_v3.csv')
col_est = ['EstablecimientoCodigo', 'EstablecimientoGlosa', 'SeremiSaludGlosa_ServicioDeSaludGlosa', 'ComunaGlosa']
col_rename = {
    'EstablecimientoCodigo': 'IdEstablecimiento',
    'EstablecimientoGlosa': 'nombre_establecimiento',
    'SeremiSaludGlosa_ServicioDeSaludGlosa': 'servicio_salud',
    'ComunaGlosa': 'comuna'
}
df_est = pd.read_excel(deis_path, sheet_name='establecimientos', usecols=col_est)
df_est = df_est.rename(columns=col_rename)
df_ms1 = df_ms.loc[df_ms.MetaSanitaria == meta_tag]
df_ms1 = df_ms1.merge(df_est, on='IdEstablecimiento', how='left')

df_ms1 = df_ms1.dropna(subset=['Ano', 'Mes'])
df_ms1['Ano'] = df_ms1['Ano'].fillna(0).astype(int)
df_ms1['Mes'] = df_ms1['Mes'].fillna(0).astype(int)
df_ms1['A\u00f1o_Mes'] = df_ms1['Ano'] * 100 + df_ms1['Mes']
df_ms1['Numerador'] = df_ms1['Numerador'].fillna(0).astype(int)
df_ms1['Denominador'] = df_ms1['Denominador'].fillna(0).astype(int)
df_ms1['IdEstablecimiento'] = df_ms1['IdEstablecimiento'].astype(str)
df_ms1['nombre_establecimiento'] = df_ms1['nombre_establecimiento'].astype(str)
df_ms1 = df_ms1.dropna(subset=["servicio_salud", "comuna"])
df_ms1["servicio_salud"] = df_ms1["servicio_salud"].fillna("No especificado").astype(str)
df_ms1['codigo_nombre'] = df_ms1['IdEstablecimiento'] + ' - ' + df_ms1['nombre_establecimiento']
df_ms1 = df_ms1.groupby(['IdEstablecimiento']).agg({
    'A\u00f1o_Mes': 'max',
    'Numerador': 'sum',
    'Denominador': 'sum',
    'codigo_nombre': 'first',
    'Dependencia Administrativa': 'first',
    'Nivel de Atenci\u00f3n': 'first',
    'comuna': 'first',
    'servicio_salud': 'first',
}).reset_index()
df_ms1['Porcentaje'] = df_ms1['Numerador'] / df_ms1['Denominador']

st.title(meta_titulo)

FILTERS = {
    "servicio_salud": "Servicio de Salud",
    "comuna": "Comuna",
    "Dependencia Administrativa": "Dependencia Administrativa",
    "Nivel de Atenci\u00f3n": "Nivel de Atenci\u00f3n",
    "codigo_nombre": "Establecimiento",
}

for col in FILTERS:
    if col not in st.session_state:
        st.session_state[col] = []

def apply_filters(df, exclude_col=None):
    df_f = df
    for col in FILTERS:
        if col == exclude_col:
            continue
        selected = st.session_state[col]
        if selected:
            df_f = df_f[df_f[col].isin(selected)]
    return df_f

st.header("Filtros")

for col, label in FILTERS.items():
    df_options = apply_filters(df_ms1, exclude_col=col)
    options = sorted(df_options[col].dropna().unique())

    st.session_state[col] = [
        v for v in st.session_state[col] if v in options
    ]

    st.multiselect(
        label,
        options,
        key=col
    )

df_ms1_filtered = apply_filters(df_ms1)

num_services = df_ms1_filtered['servicio_salud'].nunique()
num_communes = df_ms1_filtered['comuna'].nunique()
num_establishments = df_ms1_filtered['codigo_nombre'].nunique()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label='N\u00b0 Servicios de Salud', value=num_services)
with col2:
    st.metric(label='N\u00b0 de comunas', value=num_communes)
with col3:
    st.metric(label='N\u00b0 de establecimientos', value=num_establishments)

col_ms1 = ['A\u00f1o_Mes', 'codigo_nombre', 'servicio_salud', 'Numerador', 'Denominador', 'Porcentaje']
rename_ms1 = {
    'A\u00f1o_Mes': 'A\u00f1o y Mes',
    'codigo_nombre': 'Nombre del establecimiento',
    'servicio_salud': 'Servicio de Salud',
    'Numerador': 'Numerador',
    'Denominador': 'Denominador',
    'Porcentaje': 'Cumplimiento de la MS'
}
st.write(f"## Tabla de establecimientos")
st.write('A continuaci\u00f3n se muestra la tabla de los establecimientos, su numerador, denominador y cumplimiento de la meta sanitaria')
st.write(df_ms1_filtered[col_ms1].rename(columns=rename_ms1))

import io

df_export = df_ms1_filtered[col_ms1].rename(columns=rename_ms1)

output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df_export.to_excel(writer, index=False, sheet_name='Tabla_Establecimientos')

st.download_button(
    label="\U0001f4e5 Descargar tabla de establecimientos (Excel)",
    data=output.getvalue(),
    file_name="tabla_establecimientos.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

total_numerador = df_ms1_filtered['Numerador'].sum()
total_denominador = df_ms1_filtered['Denominador'].sum()
total_porcentaje = (total_numerador / total_denominador) if total_denominador > 0 else 0

st.write("## Cumplimiento de la Meta Sanitaria")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label='Numerador', value=total_numerador)
with col2:
    st.metric(label='Denominador', value=total_denominador)
with col3:
    st.metric(label='Porcentaje de cumplimiento', value=total_porcentaje)
with col4:
    st.metric(label='Meta Nacional', value=meta_nacional)

gauge_limit = int(meta_nacional * 100)
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=total_porcentaje * 100,
    title={'text': 'INDICADOR'},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "#FE6565"},
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "gray",
        'steps': [
            {'range': [0, gauge_limit], 'color': "#EAF4FA"},
            {'range': [gauge_limit, 100], 'color': "#cfe6f4"}
        ],
        'threshold': {
            'line': {'color': "black", 'width': 4},
            'thickness': 0.75,
            'value': total_porcentaje * 100
        },
        'shape': "angular"
    }
))
st.plotly_chart(fig)

df_cumplimiento = df_ms1_filtered.groupby('comuna').agg(
    total_numerador=('Numerador', 'sum'),
    total_denominador=('Denominador', 'sum')
).reset_index()

df_cumplimiento['porcentaje_cumplimiento'] = (df_cumplimiento['total_numerador'] / df_cumplimiento['total_denominador']) * 100

rename_cumplimiento = {
    'porcentaje_cumplimiento': 'Porcentaje de cumplimiento',
    'total_numerador': 'Numerador',
    'total_denominador': 'Denominador',
    'comuna': 'Comuna'
}

df_cumplimiento = df_cumplimiento.sort_values(by='porcentaje_cumplimiento', ascending=False)

st.write("## Tabla de cumplimiento por comuna")
st.write(df_cumplimiento.rename(columns=rename_cumplimiento))

fig = px.bar(
    df_cumplimiento,
    x='comuna',
    y='porcentaje_cumplimiento',
    title='Porcentaje de Cumplimiento por Comuna',
    labels={'comuna': 'Comuna', 'porcentaje_cumplimiento': 'Porcentaje de Cumplimiento'},
    text='porcentaje_cumplimiento'
)

fig.add_shape(
    type="line",
    x0=0,
    y0=gauge_limit,
    x1=len(df_cumplimiento['comuna']) - 1,
    y1=gauge_limit,
    line=dict(color="#FE6565", width=2, dash="dash"),
)

fig.update_layout(
    xaxis_title='Comuna',
    yaxis_title='Porcentaje de Cumplimiento',
    yaxis=dict(range=[0, 100])
)

st.plotly_chart(fig)
