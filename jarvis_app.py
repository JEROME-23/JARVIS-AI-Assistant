import streamlit as st
import openai
import requests
from datetime import datetime, timedelta
import re

# Configurar página
st.set_page_config(
    page_title="JARVIS v3.0 - AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar API keys
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    OPENWEATHERMAP_API_KEY = st.secrets["OPENWEATHERMAP_API_KEY"]
    NEWSAPI_KEY = st.secrets["NEWSAPI_KEY"]
    openai.api_key = OPENAI_API_KEY
except KeyError as e:
    st.error(f"⚠️ Falta API key: {e}")
    st.stop()

# Estilos
st.markdown("""
    <style>
        .jarvis-container {
            background: rgba(0, 255, 0, 0.1);
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 0 10px #00ff00;
        }
        .response-box {
            background: rgba(0, 0, 0, 0.8);
            border-left: 4px solid #00ff00;
            padding: 15px;
            margin: 10px 0;
            color: #00ff00;
        }
        h1 { color: #00ff00; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# Inicializar sesión
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'reminders' not in st.session_state:
    st.session_state.reminders = []
if 'calculations' not in st.session_state:
    st.session_state.calculations = []

# Funciones
def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=es"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return f"📍 {city}: {data['main']['temp']}°C, {data['weather'][0]['description']}. Humedad: {data['main']['humidity']}%"
        return "Ciudad no encontrada"
    except:
        return "Error al obtener clima"

def get_news(topic=""):
    try:
        query = topic if topic else "general"
        url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=es&pageSize=3&apiKey={NEWSAPI_KEY}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            articles = response.json().get('articles', [])
            if articles:
                news = "📰 Noticias:\n\n"
                for i, a in enumerate(articles[:3], 1):
                    news += f"{i}. {a['title']}\n   {a['source']['name']}\n\n"
                return news
        return "No hay noticias"
    except:
        return "Error al obtener noticias"

def get_chatgpt_response(user_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Eres JARVIS, asistente de IA profesional."}, 
                     {"role": "user", "content": user_input}],
            temperature=0.7,
            max_tokens=500
        )
        return response['choices'][0]['message']['content']
    except:
        return "Error con ChatGPT"

def calculate(expression):
    try:
        if all(c in '0123456789+-*/.() ' for c in expression):
            result = eval(expression)
            st.session_state.calculations.append(f"{expression} = {result}")
            return f"➗ {expression} = {result}"
        return "Expresión inválida"
    except ZeroDivisionError:
        return "Error: División por cero"
    except:
        return "Error en cálculo"

def add_reminder(task, days=1):
    date = (datetime.now() + timedelta(days=days)).strftime("%d/%m/%Y")
    reminder = {"task": task, "date": date, "done": False}
    st.session_state.reminders.append(reminder)
    return f"✅ Recordatorio: '{task}' para {date}"

def get_jarvis_response(user_input):
    user_lower = user_input.lower()
    
    if "clima" in user_lower or "weather" in user_lower:
        city = user_lower.split("en")[-1].strip() if "en" in user_lower else "Madrid"
        return get_weather(city)
    elif "noticias" in user_lower or "news" in user_lower:
        topic = user_lower.replace("noticias", "").replace("news", "").strip()
        return get_news(topic)
    elif "calcula" in user_lower or "calculate" in user_lower:
        return "Ve a la pestaña Calculadora"
    elif "recordatorio" in user_lower:
        return "Ve a la pestaña Recordatorios"
    elif "hora" in user_lower:
        return f"⏰ {datetime.now().strftime('%H:%M:%S')}"
    elif "fecha" in user_lower:
        return f"📅 {datetime.now().strftime('%d/%m/%Y')}"
    elif "hola" in user_lower or "buenos" in user_lower:
        return "👋 Buenos días. ¿Cómo puedo ayudarte?"
    elif "adiós" in user_lower or "bye" in user_lower:
        return "👋 Hasta pronto"
    elif "gracias" in user_lower:
        return "🙏 De nada"
    else:
        return get_chatgpt_response(user_input)

# Título
st.markdown("""
    <div class="jarvis-container">
        <h1>⚡ J.A.R.V.I.S v3.0 ⚡</h1>
        <p style="text-align: center; color: #00ff00;">ChatGPT + Clima + Noticias + Calculadora + Traductor + Búsqueda + Recordatorios</p>
    </div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🤖 Chat", "🌤️ Clima", "📰 Noticias", "🧮 Calculadora",
    "🌐 Traductor", "🔍 Búsqueda", "📌 Recordatorios", "📋 Historial"
])

with tab1:
    st.subheader("💬 Chat")
    user_input = st.text_input("Pregunta:", placeholder="Hola, Clima en Madrid, etc.")
    if user_input:
        response = get_jarvis_response(user_input)
        st.session_state.conversation_history.append({"user": user_input, "jarvis": response, "time": datetime.now().strftime("%H:%M:%S")})
        st.markdown(f'<div class="response-box">🤖 {response}</div>', unsafe_allow_html=True)

with tab2:
    st.subheader("🌤️ Clima")
    city = st.text_input("Ciudad:", value="Madrid", key="city")
    if st.button("Buscar Clima"):
        weather = get_weather(city)
        st.markdown(f'<div class="response-box">{weather}</div>', unsafe_allow_html=True)

with tab3:
    st.subheader("📰 Noticias")
    topic = st.text_input("Tema:", value="tecnología", key="topic")
    if st.button("Buscar Noticias"):
        news = get_news(topic)
        st.markdown(f'<div class="response-box">{news}</div>', unsafe_allow_html=True)

with tab4:
    st.subheader("🧮 Calculadora")
    expr = st.text_input("Expresión:", placeholder="2+2, 10*5, etc.")
    if st.button("Calcular"):
        result = calculate(expr)
        st.markdown(f'<div class="response-box">{result}</div>', unsafe_allow_html=True)
    if st.session_state.calculations:
        st.write("**Historial:**")
        for calc in st.session_state.calculations[-5:]:
            st.text(calc)

with tab5:
    st.subheader("🌐 Traductor")
    text = st.text_area("Texto:")
    lang = st.selectbox("Idioma:", ["Español", "Inglés", "Francés", "Alemán"])
    if st.button("Traducir"):
        st.info(f"Traducción a {lang}: {text}")

with tab6:
    st.subheader("🔍 Búsqueda")
    search = st.text_input("Buscar:", placeholder="Python, AI, etc.")
    if st.button("Buscar en Google"):
        st.markdown(f'🔗 [Ver en Google](https://www.google.com/search?q={search})')

with tab7:
    st.subheader("📌 Recordatorios")
    task = st.text_input("Tarea:", key="task")
    days = st.number_input("Días:", min_value=0, max_value=30, value=1)
    if st.button("Añadir Recordatorio"):
        result = add_reminder(task, days)
        st.success(result)
    
    if st.session_state.reminders:
        st.write("**Recordatorios:**")
        for i, r in enumerate(st.session_state.reminders):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(f"{'✅' if r['done'] else '⏳'} {r['task']} - {r['date']}")
            with col2:
                if st.button("✓", key=f"done_{i}"):
                    st.session_state.reminders[i]['done'] = True
                    st.rerun()

with tab8:
    st.subheader("📋 Historial")
    if st.session_state.conversation_history:
        for msg in st.session_state.conversation_history:
            st.markdown(f"<div class='response-box'><b>Tú:</b> {msg['user']}<br><b>🤖:</b> {msg['jarvis']}<br><small>⏰ {msg['time']}</small></div>", unsafe_allow_html=True)
        if st.button("Limpiar"):
            st.session_state.conversation_history = []
            st.rerun()
    else:
        st.info("Sin historial")

st.divider()
st.markdown("<p style='text-align: center; color: #00ff00; font-size: 12px;'>🤖 J.A.R.V.I.S v3.0 | Made by JEROME-23</p>", unsafe_allow_html=True)
