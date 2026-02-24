from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import settings

# 1. Usamos la URL desde los settings (centralizado y seguro)
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 2. Configuración del Engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. Sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base para los modelos
Base = declarative_base()

# NOTA: La función get_db() se ha movido a app/api/dependencies.py 
# para seguir el estándar de organización granular del template.