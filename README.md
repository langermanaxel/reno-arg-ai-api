# 🏗️ AI Construction Analysis API

API profesional diseñada para la auditoría y análisis de datos de obras civiles mediante Inteligencia Artificial. El sistema transforma reportes de obra crudos en información estructurada y accionable, detectando riesgos de seguridad y desviaciones de cronograma.

---

## 📸 Arquitectura del Sistema

La API sigue un patrón de **Persistencia en Cascada** y **Auditoría de IA**, asegurando que ningún dato se pierda incluso si el proveedor de IA falla.



---

## 🚀 Hitos del Proyecto

### 1. Normalización de Datos (Paso 2)
A diferencia de un sistema simple, esta API desacopla el **Análisis** de la **Foto de la Obra (Snapshot)**.
* **Snapshots**: Cada entrada de datos se guarda íntegramente.
* **Tablas Estructuradas**: Proyecto, Etapas, Avances y Seguridad se mapean automáticamente a columnas SQL para permitir reportes de Business Intelligence (BI).

### 2. Auditoría LLM Pro (Paso 3)
Sistema de trazabilidad total para el control de calidad y costos:
* **Track de Tokens**: Registro de consumo de entrada y salida por cada análisis.
* **Latencia**: Medición en milisegundos de la respuesta de la IA.
* **Logs de Prompts**: Almacenamiento del `System` y `User` prompt para depuración técnica.

---

## 🛠️ Stack Tecnológico

* **Backend**: FastAPI (Python 3.12+)
* **Base de Datos**: PostgreSQL
* **ORM**: SQLAlchemy 2.0 (con soporte para tipos UUID y JSON)
* **IA**: Integración con modelos GPT vía `LLMClient`
* **Logging**: Estándar profesional con trazabilidad de errores

---

## 📂 Estructura de Archivos

```text
.
├── app
│   ├── db/              # Configuración de Engine y SessionLocal
│   ├── models/          # Modelos de SQLAlchemy (analisis.py)
│   ├── schemas/         # Validaciones de Pydantic (snapshot.py)
│   ├── services/        # Lógica de LLM, PromptBuilder y Webhooks
│   └── main.py          # Orquestador y Endpoints de la API
├── requirements.txt     # Dependencias del proyecto
└── README.md            # Documentación

Gemini said
Aquí tienes el código completo en formato Markdown listo para que lo copies y lo pegues en tu archivo README.md. He estructurado la información para que se vea profesional en GitHub o cualquier plataforma de Git.

Markdown
# 🏗️ AI Construction Analysis API

API profesional diseñada para la auditoría y análisis de datos de obras civiles mediante Inteligencia Artificial. El sistema transforma reportes de obra crudos en información estructurada y accionable, detectando riesgos de seguridad y desviaciones de cronograma.

---

## 📸 Arquitectura del Sistema

La API sigue un patrón de **Persistencia en Cascada** y **Auditoría de IA**, asegurando que ningún dato se pierda incluso si el proveedor de IA falla.



---

## 🚀 Hitos del Proyecto

### 1. Normalización de Datos (Paso 2)
A diferencia de un sistema simple, esta API desacopla el **Análisis** de la **Foto de la Obra (Snapshot)**.
* **Snapshots**: Cada entrada de datos se guarda íntegramente.
* **Tablas Estructuradas**: Proyecto, Etapas, Avances y Seguridad se mapean automáticamente a columnas SQL para permitir reportes de Business Intelligence (BI).

### 2. Auditoría LLM Pro (Paso 3)
Sistema de trazabilidad total para el control de calidad y costos:
* **Track de Tokens**: Registro de consumo de entrada y salida por cada análisis.
* **Latencia**: Medición en milisegundos de la respuesta de la IA.
* **Logs de Prompts**: Almacenamiento del `System` y `User` prompt para depuración técnica.

---

## 🛠️ Stack Tecnológico

* **Backend**: FastAPI (Python 3.12+)
* **Base de Datos**: PostgreSQL
* **ORM**: SQLAlchemy 2.0 (con soporte para tipos UUID y JSON)
* **IA**: Integración con modelos GPT vía `LLMClient`
* **Logging**: Estándar profesional con trazabilidad de errores

---

## 📂 Estructura de Archivos

```text
.
├── app
│   ├── db/              # Configuración de Engine y SessionLocal
│   ├── models/          # Modelos de SQLAlchemy (analisis.py)
│   ├── schemas/         # Validaciones de Pydantic (snapshot.py)
│   ├── services/        # Lógica de LLM, PromptBuilder y Webhooks
│   └── main.py          # Orquestador y Endpoints de la API
├── requirements.txt     # Dependencias del proyecto
└── README.md            # Documentación
⚙️ Instalación y Ejecución
Activar Entorno Virtual:

Bash
source venv/bin/activate
Instalar Dependencias:

Bash
pip install -r requirements.txt
Ejecutar en Desarrollo:

Bash
uvicorn app.main:app --reload
📍 Endpoints Principales
📥 Iniciar Análisis (POST /analisis/iniciar)
Recibe el JSON de la obra, persiste los datos estructurados y dispara la IA.

🔍 Detalle de Auditoría (GET /analisis/detalle/{id})
Devuelve la radiografía completa del proceso:

Datos originales del proyecto.

Resultado de la IA (Score de coherencia, riesgos detectados).

Métricas de auditoría (Tokens usados, modelo, tiempo).

🛠️ Mantenimiento (POST /mantenimiento/reset-db)
Endpoint utilitario para limpiar y recrear el esquema de base de datos durante el desarrollo.

📊 Modelo de Datos (Snowflake Schema)
El sistema utiliza relaciones de clave foránea (FK) vinculadas al snapshot_id, lo que permite mantener un histórico de cómo evolucionó un proyecto a través de diferentes reportes.

Desarrollado con enfoque en escalabilidad y auditoría de IA.