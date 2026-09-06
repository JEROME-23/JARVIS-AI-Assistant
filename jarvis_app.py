import streamlit as st
import speech_recognition as sr
import os
from datetime import datetime
import sys

# Detectar si está en Streamlit Cloud
is_cloud = "streamlit" in sys.modules and os.getenv("STREAMLIT_SERVER_PORT") is not None

# Solo importar pyttsx3 si NO está en la nube
if not is_cloud:
    try:
        import pyttsx3
    except ImportError:
        pyttsx3 = None
else:
    pyttsx3 = None

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

if 'engine' not in st.session_state and pyttsx3 is not None:
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 120)
        engine.setProperty('volume', 0.9)
        voices = engine.getProperty('voices')
        if len(voices) > 0:
            engine.setProperty('voice', voices[0].id)
        st.session_state.engine = engine
    except Exception as e:
        st.session_state.engine = None
else:
    st.session_state.engine = None

# Título
st.markdown("""
    <div class="jarvis-container">
        <h1>⚡ J.A.R.V.I.S ⚡</h1>
        <p style="text-align: center; color: #00ff00;">
            Just A Rather Very Intelligent System
        </p>
    </div>
""", unsafe_allow_html=True)

def speak(text):
    """Hace que JARVIS hable (solo en local)"""
    if st.session_state.engine is not None:
        try:
            engine = st.session_state.engine
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            st.warning(f"⚠️ No se pudo reproducir audio: {str(e)}")
    else:
        if is_cloud:
            st.info("📱 En la nube: usa modo texto. Para escuchar, descarga la app local.")

def listen():
    """Escucha el micrófono del usuario"""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎤 Escuchando...")
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language='es-ES')
            st.success(f"✅ Escuché: {text}")
            return text
    except sr.UnknownValueError:
        st.warning("❌ No entendí lo que dijiste")
        return None
    except sr.RequestError:
        st.error("❌ Error de conexión con Google Speech Recognition")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

def get_jarvis_response(user_input):
    """Genera respuesta de JARVIS"""
    user_input_lower = user_input.lower()
    
    responses = {
        "hola": "Buenos días, señor. ¿En qué puedo serle útil?",
        "hora": f"Son las {datetime.now().strftime('%H:%M:%S')}",
        "fecha": f"Hoy es {datetime.now().strftime('%d de %B de %Y')}",
        "clima": "Lo siento señor, necesitaría conexión a datos de clima en tiempo real",
        "quién eres": "Soy JARVIS, su asistente de inteligencia artificial personal",
        "qué puedes hacer": "Puedo escuchar comandos, decirte la hora, responder preguntas y mucho más",
        "adiós": "Hasta pronto, señor",
        "gracias": "De nada, es un placer asistirle",
        "ayuda": "Puedo ayudarte con comandos de voz o texto. Prueba: 'Hola', 'Hora', 'Fecha'",
    }
    
    for keyword, response in responses.items():
        if keyword in user_input_lower:
            return response
    
    return "Entiendo, señor. He procesado su solicitud: " + user_input

# Mostrar aviso si está en la nube
if is_cloud:
    st.warning("📡 Ejecutándose en Streamlit Cloud - Modo texto disponible. Para voz, ejecuta localmente.")

tab1, tab2, tab3 = st.tabs(["🎤 Voz", "⌨️ Texto", "📋 Historial"])

with tab1:
    st.subheader("Modo Voz")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎤 Escuchar Comando", key="listen_btn", use_container_width=True):
            user_input = listen()
            if user_input:
                response = get_jarvis_response(user_input)
                st.session_state.conversation_history.append({
                    "usuario": user_input,
                    "jarvis": response,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                
                st.markdown(f'<div class="response-box"><b>JARVIS:</b> {response}</div>', 
                           unsafe_allow_html=True)
                speak(response)
    
    with col2:
        if st.button("🔇 Detener", key="stop_btn", use_container_width=True):
            st.info("Sistema pausado")

with tab2:
    st.subheader("Modo Texto")
    user_input = st.text_input("Escribe tu comando:", placeholder="¿Qué deseas saber?", key="text_input")
    
    if user_input:
        response = get_jarvis_response(user_input)
        st.session_state.conversation_history.append({
            "usuario": user_input,
            "jarvis": response,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        st.markdown(f'<div class="response-box"><b>JARVIS:</b> {response}</div>', 
                   unsafe_allow_html=True)
        
        if st.checkbox("🔊 Reproducir en voz", key="speak_checkbox"):
            speak(response)

with tab3:
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
        
        if st.button("🗑️ Limpiar Historial", use_container_width=True):
            st.session_state.conversation_history = []
            st.rerun()
    else:
        st.info("Aún no hay conversación")

# Pie de página
st.markdown("""
    <hr>
    <p style="text-align: center; color: #00ff00; font-size: 12px;">
        J.A.R.V.I.S v1.0 | Powered by Streamlit | Made with ❤️
    </p>
""", unsafe_allow_html=True)
