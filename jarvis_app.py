import streamlit as st
from datetime import datetime

# Configurar página
st.set_page_config(
    page_title="JARVIS - AI Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS
st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
            color: #00ff00;
            font-family: 'Courier New', monospace;
        }
        .jarvis-container {
            background: rgba(0, 255, 0, 0.1);
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 0 10px #00ff00;
        }
        .response-box {
            background: rgba(0, 0, 0, 0.8);
            border-left: 4px solid #00ff00;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            color: #00ff00;
        }
        h1 {
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Inicializar sesión
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Título
st.markdown("""
    <div class="jarvis-container">
        <h1>⚡ J.A.R.V.I.S ⚡</h1>
        <p style="text-align: center; color: #00ff00;">
            Just A Rather Very Intelligent System
        </p>
    </div>
""", unsafe_allow_html=True)

def get_jarvis_response(user_input):
    """Genera respuesta de JARVIS"""
    user_input_lower = user_input.lower().strip()
    
    # Base de respuestas
    responses = {
        "hola": "Buenos días, señor. ¿En qué puedo serle útil?",
        "hora": f"Son las {datetime.now().strftime('%H:%M:%S')}",
        "fecha": f"Hoy es {datetime.now().strftime('%d de %B de %Y')}",
        "clima": "Lo siento señor, necesitaría conexión a datos de clima en tiempo real",
        "quién eres": "Soy JARVIS, su asistente de inteligencia artificial personal",
        "qué puedes hacer": "Puedo responder preguntas, decirte la hora, fecha, y mantener conversaciones",
        "adiós": "Hasta pronto, señor",
        "gracias": "De nada, es un placer asistirle",
        "ayuda": "Puedo ayudarte con: Hola, Hora, Fecha, Quién eres, Qué puedes hacer, Adiós",
        "buenos días": "Buenos días, señor. ¿En qué puedo asistirle?",
        "buenas tardes": "Buenas tardes, señor. ¿En qué puedo asistirle?",
        "buenas noches": "Buenas noches, señor. ¿En qué puedo asistirle?",
    }
    
    # Buscar coincidencias exactas
    for keyword, response in responses.items():
        if keyword == user_input_lower:
            return response
    
    # Buscar coincidencias parciales
    for keyword, response in responses.items():
        if keyword in user_input_lower:
            return response
    
    # Respuesta por defecto
    return "Entiendo, señor. He procesado su solicitud: " + user_input

# Interfaz principal
st.subheader("Modo Texto - JARVIS")

# Input de usuario
user_input = st.text_input(
    "Escribe tu comando:",
    placeholder="Ejemplo: Hola, ¿Qué hora es?, ¿Quién eres?",
    key="text_input"
)

# Procesar entrada
if user_input:
    response = get_jarvis_response(user_input)
    
    # Guardar en historial
    st.session_state.conversation_history.append({
        "usuario": user_input,
        "jarvis": response,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    # Mostrar respuesta
    st.markdown(
        f'<div class="response-box"><b>🤖 JARVIS:</b> {response}</div>',
        unsafe_allow_html=True
    )

# Sección de Historial
st.divider()
st.subheader("📋 Historial de Conversación")

if st.session_state.conversation_history:
    for i, msg in enumerate(st.session_state.conversation_history, 1):
        st.markdown(f"""
            <div class="response-box">
                <b>👤 Usuario {i}:</b> {msg['usuario']}<br>
                <b>🤖 JARVIS:</b> {msg['jarvis']}<br>
                <small>⏰ {msg['timestamp']}</small>
            </div>
        """, unsafe_allow_html=True)
    
    # Botón para limpiar historial
    if st.button("🗑️ Limpiar Historial", use_container_width=True):
        st.session_state.conversation_history = []
        st.rerun()
else:
    st.info("Aún no hay conversación. ¡Escribe algo!")

# Pie de página
st.divider()
st.markdown("""
    <p style="text-align: center; color: #00ff00; font-size: 12px;">
        J.A.R.V.I.S v1.0 | Powered by Streamlit | Made with ❤️ by JEROME-23
    </p>
""", unsafe_allow_html=True)
