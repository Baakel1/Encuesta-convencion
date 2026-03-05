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
        region = st.selectbox("Región", ["Toluca", "Queretaro", "Durango", "Monterrey", "Guadalajara", "Puebla", "Tijuana", "Cancun"])
        canal = st.selectbox("Canal", ["Externo", "Marketplace"])
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

# --- DASHBOARD PRIVADO MOONLIGHT ---
st.divider()
with st.expander("🔐 Acceso Moonlight"):
    # La contraseña ahora es Moonlight922
    password = st.text_input("Introduce el código de acceso", type="password")
    
    if password == "Moonlight922": 
        st.success("Acceso autorizado. ¡Suerte en la convención, Daniel!")
        
        # Leer datos frescos para el reporte en vivo
        df_dash = conn.read(ttl=0).dropna(how="all")

        if not df_dash.empty:
            # MÉTRICAS TIPO 'KPI'
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Total Respuestas", len(df_dash))
            with col_b:
                prom_mot = df_dash["Motivacion"].mean()
                st.metric("Energía Promedio", f"{prom_mot:.1f}")
            with col_c:
                preparados = (df_dash["Impacto_Ventas"] == "Totalmente preparado").sum()
                porcentaje = (preparados / len(df_dash)) * 100
                st.metric("% Ready", f"{porcentaje:.0f}%")

            st.divider()

            # GRÁFICAS POR PREGUNTA
            st.write("### 📊 Evaluación de la Agenda")
            eval_data = {
                'Métrica': ['Claridad', 'Ponentes', 'Relevancia'],
                'Promedio': [
                    df_dash["Claridad_Objetivos"].mean(),
                    df_dash["Calidad_Ponentes"].mean(),
                    df_dash["Relevancia"].mean()
                ]
            }
            st.bar_chart(pd.DataFrame(eval_data).set_index('Métrica'))

            st.write("### 🌍 Participación por Región")
            st.bar_chart(df_dash["Región"].value_counts())

            st.write("### 🚀 Canal de Ventas")
            st.bar_chart(df_dash["Canal"].value_counts())

            # FEEDBACK ABIERTO
            st.write("### 💬 Momentos WOW (Últimos 10)")
            st.dataframe(df_dash[["Nombre", "Momento_WOW"]].tail(10), use_container_width=True)
            
        else:
            st.info("Aún no hay registros. ¡El tablero se llenará en cuanto escaneen el QR!")

