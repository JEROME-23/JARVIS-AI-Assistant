import streamlit as st
import openai
import requests
from datetime import datetime
import os

# Configurar página
st.set_page_config(
    page_title="JARVIS - AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar API keys desde Streamlit Secrets
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    OPENWEATHERMAP_API_KEY = st.secrets["OPENWEATHERMAP_API_KEY"]
    NEWSAPI_KEY = st.secrets["NEWSAPI_KEY"]
    openai.api_key = OPENAI_API_KEY
except KeyError as e:
    st.error(f"⚠️ Falta configurar la API key: {e}")
    st.stop()

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
        .error-box {
            background: rgba(255, 0, 0, 0.1);
            border-left: 4px solid #ff0000;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            color: #ff0000;
        }
        h1 {
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
            text-align: center;
        }
        .weather-box {
            background: rgba(0, 150, 255, 0.1);
            border: 2px solid #0096ff;
            border-radius: 10px;
            padding: 15px;
            color: #0096ff;
            margin: 10px 0;
        }
        .news-box {
            background: rgba(255, 200, 0, 0.1);
            border: 2px solid #ffc800;
            border-radius: 10px;
            padding: 15px;
            color: #ffc800;
            margin: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Inicializar sesión
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Título
st.markdown("""
    <div class="jarvis-container">
        <h1>⚡ J.A.R.V.I.S v2.0 ⚡</h1>
        <p style="text-align: center; color: #00ff00;">
            Just A Rather Very Intelligent System<br>
            <small>Con ChatGPT, Clima y Noticias</small>
        </p>
    </div>
""", unsafe_allow_html=True)

# Funciones para APIs
def get_weather(city):
    """Obtiene el clima actual"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=es"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            humidity = data['main']['humidity']
            return f"En {city}: {temp}°C, {description.capitalize()}. Humedad: {humidity}%"
        else:
            return "No pude obtener información del clima. Verifica el nombre de la ciudad."
    except Exception as e:
        return f"Error al obtener clima: {str(e)}"

def get_news(topic=""):
    """Obtiene las últimas noticias"""
    try:
        query = topic if topic else "general"
        url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=es&pageSize=5&apiKey={NEWSAPI_KEY}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            if articles:
                news_text = "📰 Últimas Noticias:\n\n"
                for i, article in enumerate(articles[:3], 1):
                    news_text += f"{i}. **{article['title']}**\n"
                    news_text += f"   Fuente: {article['source']['name']}\n"
                    news_text += f"   {article['description'][:100]}...\n\n"
                return news_text
            else:
                return "No encontré noticias sobre ese tema."
        else:
            return "No pude obtener las noticias en este momento."
    except Exception as e:
        return f"Error al obtener noticias: {str(e)}"

def get_chatgpt_response(user_input):
    """Obtiene respuesta de ChatGPT"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres JARVIS, un asistente de IA elegante y profesional estilo Iron Man. Responde de manera concisa y amable."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error con ChatGPT: {str(e)}"

def get_jarvis_response(user_input):
    """Genera respuesta de JARVIS con múltiples opciones"""
    user_input_lower = user_input.lower().strip()
    
    # Comandos específicos
    if "clima" in user_input_lower or "weather" in user_input_lower:
        # Extraer nombre de ciudad si está disponible
        words = user_input_lower.split()
        city = " ".join(words[words.index("en")+1:]) if "en" in words else "Madrid"
        return get_weather(city)
    
    elif "noticias" in user_input_lower or "news" in user_input_lower:
        topic = user_input_lower.replace("noticias", "").replace("news", "").strip()
        return get_news(topic)
    
    elif "hora" in user_input_lower:
        return f"Son las {datetime.now().strftime('%H:%M:%S')}"
    
    elif "fecha" in user_input_lower:
        return f"Hoy es {datetime.now().strftime('%d de %B de %Y')}"
    
    elif "quién eres" in user_input_lower or "who are you" in user_input_lower:
        return "Soy JARVIS, tu asistente de inteligencia artificial personal. Tengo acceso a ChatGPT, información de clima y noticias."
    
    elif "qué puedes hacer" in user_input_lower or "what can you do" in user_input_lower:
        return """Puedo ayudarte con:
        • Clima: Pregunta por el clima en cualquier ciudad
        • Noticias: Últimas noticias sobre cualquier tema
        • Hora y Fecha: Te digo la hora y fecha actual
        • Preguntas generales: Uso ChatGPT para respuestas inteligentes
        • Conversaciones: Podemos hablar de cualquier tema"""
    
    elif "ayuda" in user_input_lower or "help" in user_input_lower:
        return """Comandos disponibles:
        • 'Clima en [ciudad]' - Información meteorológica
        • 'Noticias sobre [tema]' - Últimas noticias
        • 'Hora' - Hora actual
        • 'Fecha' - Fecha actual
        • 'Quién eres' - Información sobre JARVIS
        • Cualquier otra pregunta será procesada por ChatGPT"""
    
    elif "hola" in user_input_lower or "buenos" in user_input_lower:
        return "Buenos días, señor. ¿En qué puedo serle útil?"
    
    elif "adiós" in user_input_lower or "bye" in user_input_lower:
        return "Hasta pronto, señor. Ha sido un placer asistirle."
    
    elif "gracias" in user_input_lower or "thanks" in user_input_lower:
        return "De nada, es un placer asistirle, señor."
    
    else:
        # Si no coincide con comandos específicos, usa ChatGPT
        return get_chatgpt_response(user_input)

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs(["🤖 Chat", "🌤️ Clima", "📰 Noticias", "📋 Historial"])

# TAB 1: Chat General
with tab1:
    st.subheader("Modo Texto Inteligente - JARVIS")
    
    user_input = st.text_input(
        "Escribe tu comando:",
        placeholder="Ejemplo: Hola, Clima en Madrid, Noticias sobre tecnología",
        key="text_input"
    )
    
    if user_input:
        with st.spinner("JARVIS procesando..."):
            response = get_jarvis_response(user_input)
        
        # Guardar en historial
        st.session_state.conversation_history.append({
            "usuario": user_input,
            "jarvis": response,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "type": "chat"
        })
        
        # Mostrar respuesta
        st.markdown(
            f'<div class="response-box"><b>🤖 JARVIS:</b> {response}</div>',
            unsafe_allow_html=True
        )

# TAB 2: Clima
with tab2:
    st.subheader("🌤️ Información Meteorológica")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        city = st.text_input("¿De qué ciudad quieres saber el clima?", value="Madrid", key="weather_city")
    with col2:
        if st.button("🔍 Buscar Clima"):
            weather_info = get_weather(city)
            st.session_state.conversation_history.append({
                "usuario": f"Clima en {city}",
                "jarvis": weather_info,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "type": "weather"
            })
            st.markdown(
                f'<div class="weather-box">{weather_info}</div>',
                unsafe_allow_html=True
            )

# TAB 3: Noticias
with tab3:
    st.subheader("📰 Últimas Noticias")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.text_input("¿Sobre qué tema quieres noticias?", value="tecnología", key="news_topic")
    with col2:
        if st.button("📰 Buscar Noticias"):
            news_info = get_news(topic)
            st.session_state.conversation_history.append({
                "usuario": f"Noticias sobre {topic}",
                "jarvis": news_info,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "type": "news"
            })
            st.markdown(
                f'<div class="news-box">{news_info}</div>',
                unsafe_allow_html=True
            )

# TAB 4: Historial
with tab4:
    st.subheader("📋 Historial de Conversación")
    
    if st.session_state.conversation_history:
        for i, msg in enumerate(st.session_state.conversation_history, 1):
            icon = "💬" if msg.get("type") == "chat" else "🌤️" if msg.get("type") == "weather" else "📰"
            st.markdown(f"""
                <div class="response-box">
                    <b>{icon} Usuario {i}:</b> {msg['usuario']}<br>
                    <b>🤖 JARVIS:</b> {msg['jarvis']}<br>
                    <small>⏰ {msg['timestamp']}</small>
                </div>
            """, unsafe_allow_html=True)
        
        if st.button("🗑️ Limpiar Historial", use_container_width=True):
            st.session_state.conversation_history = []
            st.rerun()
    else:
        st.info("Aún no hay conversación. ¡Escribe algo!")

# Pie de página
st.divider()
st.markdown("""
    <p style="text-align: center; color: #00ff00; font-size: 12px;">
        J.A.R.V.I.S v2.0 | ChatGPT + Clima + Noticias | Powered by Streamlit | Made with ❤️ by JEROME-23
    </p>
""", unsafe_allow_html=True)
