import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Izzi - Convención 2026", page_icon="🎯", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #fafafa; }
    h1, h2, h3 { color: #333333; }
    .stButton>button { 
        background-color: #EF3E42; 
        color: white; 
        border-radius: 8px; 
        width: 100%;
        height: 50px;
        font-weight: bold;
        font-size: 18px;
    }
    .stButton>button:hover { background-color: #d82c30; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
st.title("🎯 Convención de Ventas Izzi 2026")
st.write("Tu opinión es el motor de nuestra estrategia. Ayúdanos a mejorar contestando esta breve encuesta.")

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FORMULARIO ---
with st.form(key="encuesta_izzi_completa"):
    
    st.subheader("👤 Datos del Asistente")
    col1, col2 = st.columns(2)
    with col1:
        region = st.selectbox("Región", ["Norte", "Centro", "Bajío", "Occidente", "Sur"])
        canal = st.selectbox("Canal", ["Cambaceo", "Punto de Venta", "Master", "Telemarketing", "Corporativo"])
    with col2:
        puesto = st.text_input("Puesto / Rol")
        nombre = st.text_input("Nombre (Opcional)")

    st.divider()
    
    st.subheader("📊 Evaluación del Contenido")
    st.write("Califica del 1 (Pobre) al 5 (Excelente):")
    claridad = st.select_slider("Claridad de los objetivos comunicados", options=[1, 2, 3, 4, 5], value=5)
    ponentes = st.select_slider("Calidad y dominio de los ponentes", options=[1, 2, 3, 4, 5], value=5)
    relevancia = st.select_slider("Relevancia del contenido para tu día a día", options=[1, 2, 3, 4, 5], value=5)

    st.divider()

    st.subheader("🚀 Impacto Comercial")
    impacto = st.radio(
        "Después de hoy, ¿te sientes más preparado para cerrar ventas?",
        ["Totalmente preparado", "Tengo mejores bases", "Igual que antes", "Aún tengo dudas"]
    )
    motivacion = st.slider("¿Con qué nivel de energía y motivación sales del evento? (1-10)", min_value=1, max_value=10, value=10)

    st.divider()

    st.subheader("💡 Tus Ideas Cuentan")
    momento_wow = st.text_input("¿Cuál fue tu 'Momento WOW' o lo que más te gustó?")
    mejoras = st.text_area("Si pudieras cambiar una cosa para el próximo evento, ¿qué sería?")

    submit = st.form_submit_button(label="Enviar Evaluación")

# --- LÓGICA DE GUARDADO ---
if submit:
    # Diccionario con los datos exactos
    nueva_respuesta = {
        "Región": region,
        "Canal": canal,
        "Puesto": puesto,
        "Nombre": nombre,
        "Claridad_Objetivos": claridad,
        "Calidad_Ponentes": ponentes,
        "Relevancia": relevancia,
        "Impacto_Ventas": impacto,
        "Motivacion": motivacion,
        "Momento_WOW": momento_wow,
        "Mejoras": mejoras
    }
    
    try:
        # Leer datos actuales (sin nombre de pestaña para evitar errores)
        datos_existentes = conn.read(ttl=0)
        datos_existentes = datos_existentes.dropna(how="all")
        
        # Crear DataFrame y unir
        df_nuevo = pd.DataFrame([nueva_respuesta])
        datos_actualizados = pd.concat([datos_existentes, df_nuevo], ignore_index=True)
        
        # Actualizar Google Sheets
        conn.update(data=datos_actualizados)
        
        st.balloons()
        st.success("¡Información guardada con éxito! Gracias por tu tiempo.")
        
    except Exception as e:

        st.error(f"Hubo un error al guardar: {e}")
     # --- DASHBOARD PRIVADO TOTAL ---
st.divider()
with st.expander("🔐 Panel de Control Izzi (Solo Staff)"):
    password = st.text_input("Contraseña de Administrador", type="password")
    
    if password == "Izzi2026": 
        st.success("Acceso concedido. Cargando insights...")
        
        # Leer datos frescos
        df_dash = conn.read(ttl=0).dropna(how="all")

        if not df_dash.empty:
            # 1. MÉTRICAS CLAVE
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric("Total Respuestas", len(df_dash))
            with col_m2:
                prom_mot = df_dash["Motivacion"].mean()
                st.metric("Energía Promedio", f"{prom_mot:.1f}/10")

            st.divider()

            # 2. GRÁFICAS DE DATOS GENERALES
            st.write("### 🌍 Demografía y Canales")
            st.bar_chart(df_dash["Región"].value_counts())
            st.bar_chart(df_dash["Canal"].value_counts())

            # 3. EVALUACIÓN DEL CONTENIDO (Slider 1-5)
            st.write("### 📊 Evaluación (Escala 1-5)")
            # Promediamos las 3 métricas de satisfacción
            metrics_df = pd.DataFrame({
                'Métrica': ['Claridad', 'Ponentes', 'Relevancia'],
                'Promedio': [
                    df_dash["Claridad_Objetivos"].mean(),
                    df_dash["Calidad_Ponentes"].mean(),
                    df_dash["Relevancia"].mean()
                ]
            })
            st.bar_chart(metrics_df.set_index('Métrica'))

            # 4. IMPACTO COMERCIAL (Radio Button)
            st.write("### 🚀 Sentimiento de Preparación")
            impacto_counts = df_dash["Impacto_Ventas"].value_counts()
            st.bar_chart(impacto_counts)

            # 5. FEEDBACK CUALITATIVO
            st.write("### 💡 Feedback Abierto")
            tab1, tab2 = st.tabs(["WOW Moments", "Sugerencias"])
            with tab1:
                st.write(df_dash["Momento_WOW"].dropna().tail(10))
            with tab2:
                st.write(df_dash["Mejoras"].dropna().tail(10))
                
        else:
            st.info("Esperando las primeras respuestas de la convención...")
