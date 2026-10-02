# Guía de Despliegue para RAGFlow

Esta guía explica cómo aplicar el parche de interpretación de símbolos matemáticos en un servidor corriendo [RAGFlow](https://github.com/infiniflow/ragflow) de manera segura.

## El Problema
RAGFlow utiliza `pdfplumber` (que a su vez utiliza `pdfminer.six`) para extraer texto de PDFs. La versión estándar de `pdfminer.six` falla silenciosamente al parsear fuentes CMEX10 y LASY generadas por LaTeX (MacRomanEncoding sin ToUnicode CMap), resultando en la pérdida total de símbolos formales como la sumatoria (`∑`) y el producto (`∏`).

## La Solución
Instalar el fork [`Jyiro/pdfminer-lis`](https://github.com/Jyiro/pdfminer-lis) que inyecta la lista extendida de glifos TeX.

---

## Instrucciones Paso a Paso

Asumiendo que RAGFlow está corriendo mediante Docker Compose:

### 1. Conectarse al contenedor de RAGFlow

Primero, identifica el contenedor que ejecuta el servidor. Usualmente se llama `ragflow-server` o `docker-ragflow-cpu-1`.

```bash
# Ver el nombre exacto del contenedor
sudo docker ps | grep ragflow
```

### 2. Procedimiento de instalación segura (Con Rollback)

Ejecuta una sesión interactiva en el contenedor:
```bash
sudo docker exec -it docker-ragflow-cpu-1 bash
```

Adentro del contenedor, verifica la versión actual para poder hacer rollback en caso de incompatibilidad, e instala el fork:
```bash
# 1. Verificar versión actual y guardar para rollback
pip show pdfminer.six
pip freeze | grep pdfminer > /tmp/pdfminer_backup.txt

# 2. Instalar el fork
pip install git+https://github.com/Jyiro/pdfminer-lis@master

# 3. Reiniciar el servicio o contenedor (según tu setup)
```

### 3. Posibles puntos de fallo (Incompatibilidad de Versiones)

⚠️ **Cuidado:** El fork está basado en la versión más reciente del upstream (`20260108`). Si el contenedor de RAGFlow tiene una versión de `pdfminer.six` muy antigua, `pip install` podría actualizar dependencias transitivas (como `cryptography` o `charset-normalizer`) que rompan otras partes del entorno de RAGFlow.

**Alternativa Conservadora (Monkey-Patching local):**
Si detectas incompatibilidad de versiones, o no puedes actualizar la dependencia, puedes inyectar el diccionario de glifos en tiempo de ejecución sin modificar la versión instalada del paquete:

1. Copia el script `deepdoc-research/tex_glyph_patch.py` provisto en este repositorio.
2. Inyéctalo en el código base de DeepDoc antes de que inicie la extracción.
3. Importa el archivo para que el diccionario se extienda automáticamente.
