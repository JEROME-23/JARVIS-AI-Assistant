# Guía de Ejecución - JARVIS AI Assistant

## 🎯 Opción 1: En tu Computadora (La más fácil)

### Paso 1: Descargar e instalar Python
- Ve a: https://www.python.org/downloads/
- Descarga la última versión
- **IMPORTANTE**: Marca "Add Python to PATH"

### Paso 2: Descargar el código
```bash
git clone https://github.com/JEROME-23/JARVIS-AI-Assistant.git
cd JARVIS-AI-Assistant
```

### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Ejecutar JARVIS
```bash
streamlit run jarvis_app.py
```

### Paso 5: ¡Abierto!
Tu navegador se abrirá en: `http://localhost:8501`

---

## 📱 Opción 2: En tu iPhone (Mismo WiFi)

### Pasos 1-3: Igual que arriba

### Paso 4: Ejecutar con acceso de red
```bash
streamlit run jarvis_app.py --server.address 0.0.0.0
```

### Paso 5: Encontrar tu IP

**Windows:**
```bash
ipconfig
```
Busca: "IPv4 Address"

**Mac/Linux:**
```bash
ifconfig
```
Busca: "inet"

### Paso 6: En tu iPhone
- Abre Safari
- Escribe: `http://192.168.1.100:8501` (reemplaza con tu IP)

---

## 🌐 Opción 3: Desplegar en la Nube (Gratis)

### Usar Streamlit Cloud

1. Ve a: https://streamlit.io/cloud
2. Sign up con GitHub
3. New app
4. Selecciona:
   - Repository: JEROME-23/JARVIS-AI-Assistant
   - Branch: main
   - **Main file path: jarvis_app.py** ⬅️ IMPORTANTE
5. Deploy

**¡Listo!** Tu URL estará en línea en 1-2 minutos

---

## ⚡ Solución de Problemas

| Problema | Solución |
|----------|----------|
| "File does not exist" | Verifica que Main file path sea "jarvis_app.py" |
| Python no reconocido | Reinstala con "Add Python to PATH" |
| No module named streamlit | pip install streamlit |
| No micrófono | Verifica que funciona |
| No funciona en iPhone | Usa el mismo WiFi |
| Conexión rechazada | Presiona Ctrl+C y ejecuta de nuevo |