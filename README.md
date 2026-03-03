# 🏗️ AI Construction Analysis API

API profesional diseñada para la auditoría y análisis de datos de obras civiles mediante Inteligencia Artificial. El sistema transforma reportes de obra crudos en información estructurada y accionable, detectando riesgos de seguridad y desviaciones de cronograma.

---

## 📸 Arquitectura del Sistema

La API sigue un patrón de **Persistencia en Cascada** y **Auditoría de IA**, asegurando que ningún dato se pierda y que cada interacción con el LLM sea trazable.



---

## 🚀 Hitos y Capacidades

### 1. Seguridad y Usuarios
* **Hashing de Contraseñas**: Integración de `Passlib` con `Bcrypt` (v4.0.1) para proteger las credenciales.
* **Validación Rigurosa**: Uso de `EmailStr` de Pydantic para garantizar datos de contacto reales.
* **Arquitectura de Autenticación**: Sistema preparado para la implementación de JWT.

### 2. Auditoría LLM Pro
* **Track de Tokens**: Registro de consumo de entrada y salida por cada análisis.
* **Métricas de Rendimiento**: Medición de latencia y registro del modelo específico utilizado (OpenRouter).
* **Logs de Prompts**: Almacenamiento del contexto enviado a la IA para depuración técnica y mejora de prompts.

### 3. Infraestructura Profesional
* **Configuración Centralizada**: Gestión mediante `Pydantic Settings` para un manejo seguro de API Keys.
* **Docker Ready**: Incluye `Dockerfile` optimizado y `.dockerignore` para despliegues rápidos.
* **Estandard de Empaquetado**: Uso de `pyproject.toml` con soporte para herramientas de linting como `Ruff` y `Black`.

---

## 🛠️ Stack Tecnológico

* **Backend**: FastAPI (Python 3.12+)
* **Base de Datos**: PostgreSQL
* **ORM**: SQLAlchemy 2.0 (UUIDs y tipos JSON nativos)
* **IA**: Integración con OpenRouter (GPT-4, Claude, Llama 3)
* **Contenerización**: Docker (Python 3.12-slim)

---

## 📂 Estructura de Archivos

```text
.
├── app/
│   ├── api/v1/endpoints/  # Rutas de la API (analisis, usuarios)
│   ├── core/              # Configuración (config.py) y Seguridad
│   ├── db/                # Sesión y motor de base de datos
│   ├── models/            # Modelos SQLAlchemy (analisis.py, user.py)
│   ├── schemas/           # Validaciones Pydantic (snapshot.py, user.py)
│   ├── services/          # Cliente LLM y PromptBuilder
│   └── main.py            # Punto de entrada de la aplicación
├── Dockerfile             # Definición de la imagen del contenedor
├── pyproject.toml         # Metadatos y dependencias del proyecto
├── .env.example           # Plantilla de variables de entorno
└── README.md              # Esta documentación
⚙️ Instalación y Ejecución
1. Configuración Inicial
Copia el archivo de ejemplo y completa tus credenciales:

Bash
cp .env.example .env
2. Instalación (Modo Editable)
Bash
pip install -e .
3. Ejecutar con Uvicorn
Bash
uvicorn app.main:app --reload
📍 Endpoints Principales
POST /auth/register: Registra un nuevo auditor en el sistema.

POST /analisis/iniciar: Envía un snapshot de obra, lo persiste y ejecuta el análisis de IA.

GET /analisis/detalle/{id}: Devuelve la radiografía completa (datos originales + reporte de IA + métricas de auditoría).

POST /analisis/reset-db: (Dev) Limpia y recrea las tablas de la base de datos.

Desarrollado con enfoque en escalabilidad, seguridad y auditoría de IA.


---

### ¿Cómo guardarlo rápido desde la terminal?
Si quieres hacerlo sin abrir el editor, puedes usar este comando:
```bash
cat <<EOF > README.md
(Pega aquí todo el contenido de arriba)
EOF
