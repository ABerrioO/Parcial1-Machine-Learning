import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="SIATA - Monitoreo PM2.5 Valle de Aburrá",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        color: white;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.2rem;
        border-left: 5px solid #2a5298;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .status-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        color: white;
        font-weight: bold;
        display: inline-block;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0px 0px;
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

# URL API SIATA
SIATA_API_URL = "https://siata.gov.co/EntregaData1/Datos_SIATA_Aire_AQ_pm25_Last.json"

# Función para calcular ICA
def calcular_ica_pm25(valor_pm25):
    if pd.isna(valor_pm25) or valor_pm25 == -9999 or valor_pm25 < 0:
        return {
            'ica': None,
            'categoria': 'Sin dato',
            'color': 'gray',
            'hex_color': '#6c757d',
            'recomendacion': 'No hay datos disponibles para esta estación en este momento.'
        }
    
    if valor_pm25 <= 12:
        ica = (50 / 12) * valor_pm25
        categoria = 'Buena'
        color = 'green'
        hex_color = '#28a745'
        recomendacion = 'Calidad del aire satisfactoria. Actividades normales al aire libre.'
    elif valor_pm25 <= 35.4:
        ica = 50 + ((100 - 50) / (35.4 - 12)) * (valor_pm25 - 12)
        categoria = 'Aceptable'
        color = 'yellow'
        hex_color = '#ffc107'
        recomendacion = 'Personas muy sensibles deben considerar reducir la actividad prolongada al aire libre.'
    elif valor_pm25 <= 55.4:
        ica = 100 + ((150 - 100) / (55.4 - 35.4)) * (valor_pm25 - 35.4)
        categoria = 'Moderada'
        color = 'orange'
        hex_color = '#fd7e14'
        recomendacion = 'Grupos sensibles (niños, adultos mayores, enfermos respiratorios) deben evitar el ejercicio intenso al aire libre.'
    elif valor_pm25 <= 150.4:
        ica = 150 + ((200 - 150) / (150.4 - 55.4)) * (valor_pm25 - 55.4)
        categoria = 'Mala'
        color = 'red'
        hex_color = '#dc3545'
        recomendacion = 'Usar mascarilla. Población general debe limitar la exposición y evitar ejercicio al aire libre.'
    elif valor_pm25 <= 250.4:
        ica = 200 + ((300 - 200) / (250.4 - 150.4)) * (valor_pm25 - 150.4)
        categoria = 'Muy Mala'
        color = 'purple'
        hex_color = '#6f42c1'
        recomendacion = 'Permanecer en interiores con ventanas cerradas. Activar alertas de movilidad e industriales.'
    else:
        ica = 300 + ((500 - 300) / (500.4 - 250.4)) * (valor_pm25 - 250.4)
        categoria = 'Peligrosa'
        color = 'maroon'
        hex_color = '#7952b3'
        recomendacion = 'Emergencia sanitaria. Evitar cualquier tipo de exposición al aire libre.'
    
    return {
        'ica': round(ica, 1),
        'categoria': categoria,
        'color': color,
        'hex_color': hex_color,
        'recomendacion': recomendacion
    }

@st.cache_data(ttl=300)
def cargar_datos_siata():
    try:
        response = requests.get(SIATA_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data or 'measurements' not in data:
            return pd.DataFrame()
        
        mediciones = data['measurements']
        datos_procesados = []
        
        for med in mediciones:
            registro = {
                'estacion': med.get('location', 'N/A'),
                'ciudad': med.get('city', 'N/A'),
                'pais': med.get('country', 'N/A'),
                'latitud': med.get('coordinates', {}).get('latitude', None),
                'longitud': med.get('coordinates', {}).get('longitude', None),
                'pm25': med.get('value', None),
                'unidad': med.get('unit', 'µg/m³'),
                'parametro': med.get('parameter', 'pm25'),
                'fecha_utc': med.get('date', {}).get('utc', None),
                'fecha_local': med.get('date', {}).get('local', None),
                'periodo_promedio_horas': med.get('averagingPeriod', {}).get('value', 1),
                'fuente': med.get('sourceName', 'SIATA'),
                'tipo_fuente': med.get('sourceType', 'government')
            }
            datos_procesados.append(registro)
        
        df = pd.DataFrame(datos_procesados)
        df['fecha_utc'] = pd.to_datetime(df['fecha_utc'], errors='coerce')
        df['fecha_local'] = pd.to_datetime(df['fecha_local'], errors='coerce')
        
        # Aplicar cálculo de ICA
        resultados_ica = df['pm25'].apply(calcular_ica_pm25)
        df['ica'] = resultados_ica.apply(lambda x: x['ica'])
        df['categoria'] = resultados_ica.apply(lambda x: x['categoria'])
        df['color'] = resultados_ica.apply(lambda x: x['color'])
        df['hex_color'] = resultados_ica.apply(lambda x: x['hex_color'])
        df['recomendacion'] = resultados_ica.apply(lambda x: x['recomendacion'])
        
        return df
    except Exception as e:
        st.error(f"Error al conectar con la API de SIATA: {e}")
        return pd.DataFrame()

# Cargar datos
df_siata = cargar_datos_siata()

# Header Principal
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 2.2rem;">🍃 Sistema de Monitoreo de Calidad del Aire (PM2.5)</h1>
    <p style="margin:0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
        Plataforma de Análisis Predictivo y Prescriptivo del Valle de Aburrá - Datos SIATA en Tiempo Real
    </p>
</div>
""", unsafe_allow_html=True)

if df_siata.empty:
    st.warning("No se pudieron cargar los datos de la API en este momento. Intenta refrescar la página.")
else:
    # Sidebar
    st.sidebar.image("https://siata.gov.co/sitio_web/assets/img/logo_siata.png", width=180) if False else None
    st.sidebar.title("🔍 Filtros y Configuración")
    
    ciudades = ["Todas"] + sorted(list(df_siata['ciudad'].dropna().unique()))
    ciudad_sel = st.sidebar.selectbox("Filtrar por Municipio / Ciudad:", ciudades)
    
    categorias = ["Todas"] + ["Buena", "Aceptable", "Moderada", "Mala", "Muy Mala", "Peligrosa", "Sin dato"]
    categoria_sel = st.sidebar.selectbox("Filtrar por Categoría ICA:", categorias)
    
    # Aplicar Filtros
    df_filtrado = df_siata.copy()
    if ciudad_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado['ciudad'] == ciudad_sel]
    if categoria_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_sel]

    # Datos Válidos para métricas
    df_validos = df_filtrado[(df_filtrado['pm25'] != -9999) & (df_filtrado['pm25'].notna())]

    # Métrica resumen superior
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Estaciones Totales", len(df_filtrado))
    col2.metric("Estaciones Activas", len(df_validos))
    col3.metric("Promedio PM2.5", f"{df_validos['pm25'].mean():.1f} µg/m³" if not df_validos.empty else "N/A")
    col4.metric("Máximo PM2.5", f"{df_validos['pm25'].max():.1f} µg/m³" if not df_validos.empty else "N/A")
    col5.metric("Mínimo PM2.5", f"{df_validos['pm25'].min():.1f} µg/m³" if not df_validos.empty else "N/A")

    st.markdown("---")

    # PESTAÑAS PRINCIPALES
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺️ Mapa Interactivo", 
        "📊 Análisis Estadístico", 
        "🔴 Sistema de Alertas", 
        "📋 Consulta por Estación", 
        "ℹ️ Marco Teórico & Proyecto"
    ])

    # ---------------------------------------------------------
    # TAB 1: MAPA INTERACTIVO
    # ---------------------------------------------------------
    with tab1:
        st.subheader("Ubicación Geográfica y Estado de Calidad del Aire")
        st.write("Visualización espacial de los sensores de monitoreo de PM2.5 en el Valle de Aburrá.")
        
        df_mapa = df_filtrado[(df_filtrado['latitud'].notna()) & (df_filtrado['longitud'].notna())]
        
        if not df_mapa.empty:
            centro_lat = df_mapa['latitud'].mean()
            centro_lon = df_mapa['longitud'].mean()
            
            mapa = folium.Map(location=[centro_lat, centro_lon], zoom_start=11, tiles="OpenStreetMap")
            marker_cluster = MarkerCluster().add_to(mapa)
            
            for _, row in df_mapa.iterrows():
                popup_html = f"""
                <div style="font-family: Arial; font-size: 13px; width: 230px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e3c72;">{row['estacion']}</h4>
                    <b>Ciudad:</b> {row['ciudad']}<br/>
                    <b>PM2.5:</b> {row['pm25']:.1f} µg/m³<br/>
                    <b>ICA:</b> {row['ica'] if row['ica'] else 'N/A'}<br/>
                    <b>Categoría:</b> <span style="color:{row['hex_color']}; font-weight:bold;">{row['categoria']}</span><br/>
                    <hr style="margin:8px 0;"/>
                    <small><i>{row['recomendacion']}</i></small>
                </div>
                """
                folium.Marker(
                    location=[row['latitud'], row['longitud']],
                    popup=folium.Popup(popup_html, max_width=260),
                    icon=folium.Icon(color=row['color'] if row['color'] in ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'gray'] else 'info-sign', icon='info-sign'),
                    tooltip=f"{row['estacion']} ({row['categoria']})"
                ).add_to(marker_cluster)
            
            st_folium(mapa, width="100%", height=500)
        else:
            st.warning("No hay datos geográficos disponibles para los filtros seleccionados.")

    # ---------------------------------------------------------
    # TAB 2: ANÁLISIS ESTADÍSTICO
    # ---------------------------------------------------------
    with tab2:
        st.subheader("Análisis Exploratorio de Datos (EDA)")
        
        if not df_validos.empty:
            c1, c2 = st.columns(2)
            
            with c1:
                # Distribución ICA por Categoría
                cat_counts = df_filtrado['categoria'].value_counts().reset_index()
                cat_counts.columns = ['Categoría', 'Cantidad']
                
                color_map = {
                    'Buena': '#28a745',
                    'Aceptable': '#ffc107',
                    'Moderada': '#fd7e14',
                    'Mala': '#dc3545',
                    'Muy Mala': '#6f42c1',
                    'Peligrosa': '#7952b3',
                    'Sin dato': '#6c757d'
                }
                
                fig_cat = px.bar(
                    cat_counts, 
                    x='Categoría', 
                    y='Cantidad',
                    color='Categoría',
                    color_discrete_map=color_map,
                    title="Distribución de Estaciones por Categoría de ICA",
                    text_auto=True
                )
                fig_cat.update_layout(showlegend=False)
                st.plotly_chart(fig_cat, use_container_width=True)

            with c2:
                # Top 10 Estaciones más contaminadas
                top10 = df_validos.nlargest(10, 'pm25')
                fig_top10 = px.bar(
                    top10,
                    y='estacion',
                    x='pm25',
                    color='categoria',
                    color_discrete_map=color_map,
                    orientation='h',
                    title="Top 10 Estaciones con Mayor PM2.5 (µg/m³)",
                    labels={'pm25': 'PM2.5 (µg/m³)', 'estacion': 'Estación'}
                )
                fig_top10.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_top10, use_container_width=True)

            st.markdown("---")
            c3, c4 = st.columns(2)
            
            with c3:
                # Histograma PM2.5
                fig_hist = px.histogram(
                    df_validos,
                    x='pm25',
                    nbins=20,
                    title="Distribución de Concentraciones PM2.5",
                    color_discrete_sequence=['#2a5298'],
                    marginal="box"
                )
                fig_hist.add_vline(x=df_validos['pm25'].mean(), line_dash="dash", line_color="red", annotation_text="Media")
                fig_hist.add_vline(x=df_validos['pm25'].median(), line_dash="dash", line_color="green", annotation_text="Mediana")
                st.plotly_chart(fig_hist, use_container_width=True)

            with c4:
                # Comparativo por Ciudad / Municipio
                if 'ciudad' in df_validos.columns:
                    city_avg = df_validos.groupby('ciudad')['pm25'].mean().reset_index()
                    fig_city = px.bar(
                        city_avg,
                        x='ciudad',
                        y='pm25',
                        title="Promedio de PM2.5 por Municipio / Sector",
                        color='pm25',
                        color_continuous_scale='Reds'
                    )
                    st.plotly_chart(fig_city, use_container_width=True)

    # ---------------------------------------------------------
    # TAB 3: SISTEMA DE ALERTAS TEMPRANAS
    # ---------------------------------------------------------
    with tab3:
        st.subheader("🚨 Sistema Prescriptivo de Alertas Tempranas")
        st.write("Evaluación automática del nivel de riesgo para la salud pública según la calidad del aire.")
        
        alertas_roja = df_filtrado[df_filtrado['categoria'].isin(['Mala', 'Muy Mala', 'Peligrosa'])]
        alertas_naranja = df_filtrado[df_filtrado['categoria'] == 'Moderada']
        alertas_amarilla = df_filtrado[df_filtrado['categoria'] == 'Aceptable']
        alertas_verde = df_filtrado[df_filtrado['categoria'] == 'Buena']

        st.markdown(f"### 🔴 Alerta Crítica (Mala / Muy Mala / Peligrosa): `{len(alertas_roja)}` estaciones")
        if not alertas_roja.empty:
            for _, r in alertas_roja.iterrows():
                st.error(f"""
                **Estación:** {r['estacion']} ({r['ciudad']})  
                **PM2.5:** {r['pm25']} µg/m³ | **ICA:** {r['ica']} | **Categoría:** {r['categoria']}  
                💡 **Recomendación:** {r['recomendacion']}
                """)
        else:
            st.success("No hay estaciones en nivel de Alerta Roja actualmente.")

        st.markdown(f"### 🟠 Alerta Moderada: `{len(alertas_naranja)}` estaciones")
        if not alertas_naranja.empty:
            with st.expander("Ver estaciones en Alerta Moderada"):
                for _, r in alertas_naranja.iterrows():
                    st.warning(f"**{r['estacion']}** ({r['ciudad']}) - PM2.5: {r['pm25']} µg/m³ | ICA: {r['ica']}")
        
        st.markdown(f"### 🟢 Estado Normal / Aceptable: `{len(alertas_amarilla) + len(alertas_verde)}` estaciones")

    # ---------------------------------------------------------
    # TAB 4: CONSULTA Y TABLA DE DATOS
    # ---------------------------------------------------------
    with tab4:
        st.subheader("📋 Registro Completo de Estaciones de Monitoreo")
        
        search_term = st.text_input("🔎 Buscar estación por nombre o ubicación:")
        df_tabla = df_filtrado.copy()
        if search_term:
            df_tabla = df_tabla[df_tabla['estacion'].str.contains(search_term, case=False, na=False)]
        
        st.dataframe(
            df_tabla[['estacion', 'ciudad', 'pm25', 'ica', 'categoria', 'fecha_local', 'recomendacion']],
            use_container_width=True,
            height=400
        )
        
        # Descarga CSV
        csv = df_tabla.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Datos en CSV",
            data=csv,
            file_name=f"calidad_aire_siata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    # ---------------------------------------------------------
    # TAB 5: MARCO TEÓRICO Y PROYECTO
    # ---------------------------------------------------------
    with tab5:
        st.markdown("""
        ### 📚 Marco Teórico y Contexto del Proyecto
        
        #### **1. Situación Problema**
        La Secretaría de Salud Municipal de Medellín y los organismos ambientales del Valle de Aburrá requieren un sistema de apoyo a la decisión en tiempo real para identificar zonas críticas de contaminación por material particulado **PM2.5** y emitir recomendaciones preventivas a la población vulnerable.

        #### **2. ¿Qué es el PM2.5 y el ICA?**
        * **PM2.5:** Partículas suspendidas en el aire con un diámetro inferior a 2.5 micrómetros. Pueden penetrar profundamente en los pulmones e ingresar al torrente sanguíneo.
        * **Índice de Calidad del Aire (ICA):** Escala estandarizada (basada en la EPA y SIATA) que categoriza el estado del aire:
        
        | Rango ICA | Categoría | Color | Impacto en Salud |
        |---|---|---|---|
        | 0 - 50 | Buena | Verde | Sin riesgo para la salud |
        | 51 - 100 | Aceptable | Amarillo | Aceptable; posible riesgo para personas muy sensibles |
        | 101 - 150 | Moderada | Naranja | Grupos sensibles pueden experimentar efectos |
        | 151 - 200 | Mala | Rojo | Toda la población puede comenzar a sentir efectos |
        | 201 - 300 | Muy Mala | Morado | Alerta de salud para toda la población |
        | > 300 | Peligrosa | Marrón | Condiciones de emergencia sanitaria |

        #### **3. Fuente de Datos**
        Los datos son obtenidos directamente de la API pública en tiempo real de **SIATA** (Sistema de Alerta Temprana de Medellín y el Valle de Aburrá):
        `https://siata.gov.co/EntregaData1/Datos_SIATA_Aire_AQ_pm25_Last.json`
        """)

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Sistema desarrollado con Streamlit | Datos oficiales de SIATA</p>", unsafe_allow_html=True)
