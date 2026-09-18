# 🍃 Monitoreo de Calidad del Aire PM2.5 - Valle de Aburrá (SIATA)

Aplicación web desarrollada en **Streamlit** para el monitoreo, visualización geográfica, análisis exploratorio de datos y sistema de alertas tempranas del material particulado PM2.5 en los municipios del Valle de Aburrá, consumiendo la API oficial en tiempo real del **SIATA** (Sistema de Alerta Temprana de Medellín y el Valle de Aburrá).

---

## 🚀 Características Principal de la Aplicación

- 🗺️ **Mapa Interactivo (Folium):** Ubicación geográfica en tiempo real de todas las estaciones de monitoreo con estado de calidad del aire y recomendaciones prescriptivas.
- 📊 **Análisis Estadístico Avanzado (Plotly):** Gráficos dinámicos e interactivos de la distribución de PM2.5, categorías ICA, boxplots e histogramas.
- 🔴 **Sistema Prescriptivo de Alertas Tempranas:** Categorización automática de niveles de riesgo (Mala, Muy Mala, Peligrosa) con recomendaciones para salud pública.
- 📋 **Búsqueda y Descarga de Datos:** Filtros por municipio, estación y categoría, con opción de descarga en formato CSV.
- 📚 **Marco Teórico:** Explicación detallada de los rangos ICA (Índice de Calidad del Aire) y PM2.5.

---

## 🛠️ Instalación y Ejecución Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   cd TU_REPOSITORIO
   ```

2. **Crear y activar un entorno virtual (opcional pero recomendado):**
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```

3. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación:**
   ```bash
   streamlit run app.py
   ```

---

## ☁️ Despliegue en Streamlit Community Cloud

Para desplegar la aplicación de forma gratuita en [Streamlit Community Cloud](https://streamlit.io/cloud):

1. Sube estos archivos a tu repositorio de **GitHub**.
2. Ingresa a tu cuenta en [Streamlit Cloud](https://share.streamlit.io/).
3. Haz clic en **"New app"**.
4. Selecciona tu repositorio de GitHub, la rama (normalmente `main` o `master`) y el archivo principal (`app.py`).
5. Haz clic en **"Deploy!"**.
6. Resultado: Página desplegada en streamlit.io: https://parcial1-machine-learning-esx6eg8sf4hhjomcfh3hc2.streamlit.app

---

## 📄 Estructura del Repositorio

```text
├── app.py                      # Código principal de la aplicación Streamlit
├── requirements.txt            # Librerías y dependencias necesarias
├── README.md                   # Documentación del proyecto
├── Parcial1.ipynb              # Cuaderno Jupyter de análisis exploratorio inicial
└── landing_page_siata.html     # Landing page HTML informativa
```

---

## 📡 Fuente de Datos
- **SIATA:** API de calidad del aire para PM2.5 en tiempo real (`https://siata.gov.co/EntregaData1/Datos_SIATA_Aire_AQ_pm25_Last.json`).
