# RENO Studio AI - Construction Audit API

API profesional modularizada para la generación de informes narrativos de auditoría técnica en obras de construcción utilizando IA.

## 🏗️ Arquitectura
El proyecto utiliza una **Arquitectura de Capas** desacoplada:
- **Core**: Configuración y base de datos.
- **Services**: Lógica de negocio e integración con LLM.
- **Repositories**: Capa de persistencia (Unit of Work).
- **Models/Schemas**: Definición de datos y validación.

## 🛠️ Instalación Rápida (Docker)

1. Clonar y entrar al proyecto:
   ```bash
   git clone <repo-url>
   cd reno-studio-ai
Crear archivo .env basado en env.example y agregar tu OPENROUTER_API_KEY.

Levantar con Docker Compose:

Bash
docker-compose up --build
La API estará disponible en http://localhost:8000 y la documentación interactiva en /docs.

🧪 Testing
Para correr pruebas locales sin Docker:

Bash
pip install -r requirements.txt
uvicorn main:app --reload