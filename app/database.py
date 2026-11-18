from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from .config import settings


class Base(DeclarativeBase):
    pass


cfg = settings()

# FRAUDSHIELD POSTGRESQL CONFIGURATION V1
import os as _fraudshield_os
from sqlalchemy import create_engine as _fraudshield_engine_factory

def _fraudshield_initialize_engine():
    override = _fraudshield_os.environ.get(
        "FRAUDSHIELD_DATABASE_URL"
    )

    if override:
        if not override.startswith("postgresql+psycopg://"):
            raise RuntimeError(
                "Unsupported FraudShield database driver."
            )

        return _fraudshield_engine_factory(
            override,
            pool_pre_ping=True,
            hide_parameters=True,
            connect_args={"connect_timeout": 10}
        )

    return create_engine(cfg.database_url, connect_args={'check_same_thread': False} if cfg.database_url.startswith('sqlite') else {}, pool_pre_ping=True)

engine = _fraudshield_initialize_engine()
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as db:
        yield db
