import streamlit as st
import requests
import google.generativeai as genai
import json
from datetime import datetime, timedelta

# Configurar página
st.set_page_config(
    page_title="JARVIS v3.0 - AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar API keys
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    OPENWEATHERMAP_API_KEY = st.secrets["OPENWEATHERMAP_API_KEY"]
    NEWSAPI_KEY = st.secrets["NEWSAPI_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
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
    except Exception:
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
    except Exception:
        return "Error al obtener noticias"


def parse_json_response(text):
    try:
        cleaned = text.strip()
        if "```" in cleaned:
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
        if cleaned.startswith("{") and cleaned.endswith("}"):
            return json.loads(cleaned)
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(cleaned[start:end+1])
    except Exception:
        pass
    return {"intent": "general", "confidence": 0.0}


def detect_intent(user_input, history=None):
    try:
        history = history or []
        context = ""
        if history:
            recent = history[-5:]
            context = "\n".join(
                f"Usuario: {item['user']}\nJARVIS: {item['jarvis']}" for item in recent
            )

        prompt = f"""
        Analiza la intención del usuario usando el contexto de la conversación.
        Devuelve SOLO un JSON válido con este formato exacto:
        {{"intent":"clima|noticias|calculo|recordatorio|hora|fecha|saludo|despedida|gracias|general","city":"ciudad si aplica","topic":"tema si aplica","task":"tarea si aplica","confidence":0.0-1.0}}

        Contexto previo:
        {context}

        Usuario: {user_input}
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return parse_json_response(response.text)
    except Exception:
        user_lower = user_input.lower()
        if "clima" in user_lower or "weather" in user_lower:
            return {"intent": "clima", "city": "Madrid", "confidence": 0.9}
        if "noticias" in user_lower or "news" in user_lower:
            return {"intent": "noticias", "topic": "tecnología", "confidence": 0.9}
        if "calcula" in user_lower or "calculate" in user_lower:
            return {"intent": "calculo", "confidence": 0.9}
        if "recordatorio" in user_lower or "reminder" in user_lower:
            return {"intent": "recordatorio", "confidence": 0.9}
        if "hora" in user_lower:
            return {"intent": "hora", "confidence": 0.9}
        if "fecha" in user_lower:
            return {"intent": "fecha", "confidence": 0.9}
        if "hola" in user_lower or "buenos" in user_lower or "buenas" in user_lower:
            return {"intent": "saludo", "confidence": 0.9}
        if "adiós" in user_lower or "bye" in user_lower or "adios" in user_lower:
            return {"intent": "despedida", "confidence": 0.9}
        if "gracias" in user_lower:
            return {"intent": "gracias", "confidence": 0.9}
        return {"intent": "general", "confidence": 0.0}


def get_gemini_response(user_input, history=None):
    try:
        history = history or []
        context = ""
        if history:
            recent = history[-6:]
            context = "\n".join(
                f"Usuario: {item['user']}\nJARVIS: {item['jarvis']}" for item in recent
            )

        system_instruction = """
        Eres JARVIS, un asistente inteligente, profesional y avanzado.
        Responde en español.
        Usa el contexto previo de la conversación.
        Si falta información, pregunta una aclaración breve.
        Si es posible, responde con estructura clara, útil y profunda.
        Mantén una personalidad técnica, elegante y útil.
        """

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )

        prompt = f"""
        Contexto de la conversación:
        {context}

        Usuario: {user_input}
        """

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error con Gemini: {e}"


def calculate(expression):
    try:
        if all(c in '0123456789+-*/.() ' for c in expression):
            result = eval(expression)
            st.session_state.calculations.append(f"{expression} = {result}")
            return f"➗ {expression} = {result}"
        return "Expresión inválida"
    except ZeroDivisionError:
        return "Error: División por cero"
    except Exception:
        return "Error en cálculo"


def add_reminder(task, days=1):
    date = (datetime.now() + timedelta(days=days)).strftime("%d/%m/%Y")
    reminder = {"task": task, "date": date, "done": False}
    st.session_state.reminders.append(reminder)
    return f"✅ Recordatorio: '{task}' para {date}"


def get_jarvis_response(user_input):
    history = st.session_state.conversation_history
    intent_data = detect_intent(user_input, history)
    intent = intent_data.get("intent", "general")

    if intent == "clima":
        city = intent_data.get("city") or "Madrid"
        return get_weather(city)
    elif intent == "noticias":
        topic = intent_data.get("topic") or "tecnología"
        return get_news(topic)
    elif intent == "calculo":
        return "Ve a la pestaña Calculadora"
    elif intent == "recordatorio":
        return "Ve a la pestaña Recordatorios"
    elif intent == "hora":
        return f"⏰ {datetime.now().strftime('%H:%M:%S')}"
    elif intent == "fecha":
        return f"📅 {datetime.now().strftime('%d/%m/%Y')}"
    elif intent == "saludo":
        return "👋 Buenos días. ¿Cómo puedo ayudarte?"
    elif intent == "despedida":
        return "👋 Hasta pronto"
    elif intent == "gracias":
        return "🙏 De nada"
    else:
        return get_gemini_response(user_input, history)


# Título
st.markdown("""
    <div class="jarvis-container">
        <h1>⚡ J.A.R.V.I.S v3.0 ⚡</h1>
        <p style="text-align: center; color: #00ff00;">Gemini + Clima + Noticias + Calculadora + Traductor + Búsqueda + Recordatorios</p>
    </div>
""", unsafe_allow_html=True)

# Tabs

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🤖 Chat", "🌤️ Clima", "📰 Noticias", "🧮 Calculadora",
    "🌐 Traductor", "🔍 Búsqueda", "📌 Recordatorios", "📋 Historial"
])

with tab1:
    st.subheader("💬 Chat")
    user_input = st.text_input("Pregunta:", placeholder="Hola, clima en Madrid, etc.")
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
