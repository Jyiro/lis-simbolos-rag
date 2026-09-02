# Configuración RAGFlow (Fase 3)

Este documento detalla la arquitectura híbrida para probar el pipeline de RAGFlow conectando el LLM remoto (Kaggle) con el modelo de Embedding local.

## Arquitectura

```text
┌────────────────────────────────────────────────────────┐
│                    RAGFlow (local)                     │
│                                                        │
│   Chat LLM ───→ Ngrok ───→ Kaggle (llama_cpp.server)   │
│   Embedding ──→ Ollama local (nomic-embed-text)        │
└────────────────────────────────────────────────────────┘
```

---

## 1. Servidor de Embedding (Local)

El modelo de embedding (`nomic-embed-text`) corre localmente en tu computadora. No necesita GPU y es extremadamente rápido.

1. Instalar Ollama en tu sistema (si no lo tenés).
2. Arrancar el servicio Ollama escuchando en todas las interfaces de red (necesario para Docker/RAGFlow):
   ```bash
   OLLAMA_HOST=0.0.0.0 ollama serve
   ```
3. Descargar el modelo (en otra terminal):
   ```bash
   ollama pull nomic-embed-text
   ```

---

## 2. Servidor de LLM (Kaggle remota)

Para evitar que la URL de Ngrok cambie cada vez que cambias de modelo LLM, **debés separar el código en dos celdas de Kaggle diferentes**.

### Celda 1: Túnel Ngrok (Correr UNA vez)
```python
!pip install pyngrok -q
from pyngrok import ngrok

NGROK_TOKEN = "TU_TOKEN_AQUI"
ngrok.set_auth_token(NGROK_TOKEN)

for tunnel in ngrok.get_tunnels():
    ngrok.disconnect(tunnel.public_url)

public_url = ngrok.connect(8000)
print("=" * 60)
print(f"🔥 URL FIJA PARA ESTA SESIÓN: {public_url.public_url}/v1")
print("=" * 60)
print("Copiá esta URL en RAGFlow. No vuelvas a correr esta celda.")
```

### Celda 2: Servidor LLM (Correr, parar y cambiar cuantas veces quieras)
```python
# Cambiá el modelo descomentando la línea deseada
MODEL = "/kaggle/input/models/jonsceballos/qwen3-5-2b/gguf/default/1/Qwen3.5-2B-Q4_K_M.gguf"

!python -m llama_cpp.server \
    --model {MODEL} \
    --host 0.0.0.0 \
    --port 8000 \
    --n_gpu_layers -1 \
    --n_ctx 8192 \
    --embedding
```

---

## 3. Configuración en la UI de RAGFlow

Ve a **Settings → Model Providers**.

### Provider 1: Chat LLM
- **Provider:** OpenAI-API-Compatible
- **Instance Name:** `kaggle-llm`
- **Base URL:** `https://TU-URL.ngrok-free.app/v1` *(La que te dio la Celda 1)*
- **API Key:** `local`

> Luego de agregarlo, hacé clic en **Add LLM Model**. Poné el nombre exacto del archivo GGUF (ej: `Qwen3.5-2B-Q4_K_M`), tipo `chat`, Max Tokens `8192`.

### Provider 2: Embedding
- **Provider:** Ollama
- **Instance Name:** `local-ollama`
- **Base URL:** `http://172.17.0.1:11434` *(IP del puente Docker, o la IP LAN de tu PC, ej: 172.16.80.105)*
- **API Key:** *(vacio)*

> Luego de agregarlo, hacé clic en **Add Embedding Model**. Nombre: `nomic-embed-text`, tipo `embedding`.

---

## 4. Crear Base de Conocimiento (Knowledge Base)

1. En RAGFlow, ve a **Knowledge Base → + Create**.
2. **Nombre:** `corpus-ragflow-simbolos`
3. **Embedding Model:** `nomic-embed-text`
4. **Chunk Method:** `Paper`
5. **Subir los 4 PDFs** que se encuentran en `dataset-ragflow/corpus-ragflow/`.
6. Haz clic en el botón "Play" para procesarlos (parsing y embedding).

## 5. Preguntas de Prueba en el Chat

Crea un chat asociado a la Base de Conocimiento y probá estas consultas para auditar la preservación de los símbolos:

* **Símbolo □:** *"Según el texto de redes neuronales y lógica modal, ¿qué representa el operador □ (cuadrado) y cómo se diferencia de una proposición normal?"*
* **Símbolo ⊂:** *"En el libro de Álgebra Abstracta, ¿qué significa exactamente el símbolo ⊂? Si tengo A ⊂ B y B ⊂ A simultáneamente, ¿qué se puede concluir según el autor?"*

> **Atención Analítica:** Si el parser omitió silenciosamente los símbolos (verificable haciendo clic en las citas de los chunks), el modelo presentará alucinaciones paramétricas, comprobando la hipótesis central de vulnerabilidad en la Fase 1.

---

## 6. To do next (Próximos pasos de investigación)

Para continuar profundizando en la vulnerabilidad descubierta, se deben abordar los siguientes puntos:

1. **Auditoría de Configuración y Parsing en RAGFlow:**
   - Entender los parámetros de configuración avanzados.
   - Ver qué opciones de "Chunk Method" (ej. *Paper*, *General*, *QA*) se pueden toquetear en la interfaz para mitigar el problema.
   - Averiguar en detalle técnico cuál es el motor/librería de parsing de PDFs que usa RAGFlow por detrás (ej. OCR, PyMuPDF, pdfplumber) y por qué falla con fuentes matemáticas y caracteres Unicode específicos.

2. **Mapeo de Rupturas y Estrategias de Mitigación:**
   - Determinar una taxonomía exacta de **qué símbolos específicos son los que se rompen** (ej. Blackboard bold como `ℤ`, operadores modales como `□`/`◇`, cuantificadores, relaciones como `⊳`).
   - Investigar **cómo se puede arreglar** este Punto de Falla 1 (ej. ¿Se requiere un OCR matemático como Nougat o Mathpix antes del embedding? ¿Se puede corregir mediante metadatos o limpieza pre-procesada de los chunks?).
