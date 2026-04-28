from pathlib import Path

from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.models import Agent, Skill, Tool, User
from app.services.auth import hash_password
from app.services.user_asset_bootstrap import UserAssetBootstrapService


def init_db() -> None:
    migrate_user_ids_to_uuid()
    Base.metadata.create_all(bind=engine)
    seed_default_admin()
    normalize_asset_storage_paths()


def migrate_user_ids_to_uuid() -> None:
    if engine.dialect.name != "postgresql":
        return

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    if "users" not in existing_tables:
        return

    with engine.begin() as connection:
        column_type = connection.execute(
            text(
                """
                SELECT data_type
                FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'id'
                """
            )
        ).scalar_one_or_none()
        if column_type == "uuid":
            return

        connection.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
        connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS id_uuid uuid"))
        connection.execute(text("UPDATE users SET id_uuid = gen_random_uuid() WHERE id_uuid IS NULL"))
        migrate_user_storage_paths(connection)

        for table_name, old_column, new_column in [
            ("agents", "owner_user_id", "owner_user_id_uuid"),
            ("skills", "owner_user_id", "owner_user_id_uuid"),
            ("tools", "owner_user_id", "owner_user_id_uuid"),
            ("conversations", "user_id", "user_id_uuid"),
            ("job_runs", "user_id", "user_id_uuid"),
            ("audit_logs", "user_id", "user_id_uuid"),
            ("messages", "sender_id", "sender_id_uuid"),
        ]:
            if table_name not in existing_tables:
                continue
            connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {new_column} uuid"))
            connection.execute(
                text(
                    f"""
                    UPDATE {table_name} AS child
                    SET {new_column} = users.id_uuid
                    FROM users
                    WHERE child.{old_column} = users.id
                    """
                )
            )

        for table_name, constraint_name in [
            ("agents", "agents_owner_user_id_fkey"),
            ("skills", "skills_owner_user_id_fkey"),
            ("tools", "tools_owner_user_id_fkey"),
            ("conversations", "conversations_user_id_fkey"),
            ("job_runs", "job_runs_user_id_fkey"),
            ("audit_logs", "audit_logs_user_id_fkey"),
        ]:
            if table_name not in existing_tables:
                continue
            connection.execute(text(f"ALTER TABLE ONLY {table_name} DROP CONSTRAINT IF EXISTS {constraint_name}"))

        connection.execute(text("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_pkey"))
        connection.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS id"))
        connection.execute(text("ALTER TABLE users RENAME COLUMN id_uuid TO id"))
        connection.execute(text("ALTER TABLE users ADD CONSTRAINT users_pkey PRIMARY KEY (id)"))

        for table_name, old_column, new_column, fk_name, needs_index in [
            ("agents", "owner_user_id", "owner_user_id_uuid", "agents_owner_user_id_fkey", True),
            ("skills", "owner_user_id", "owner_user_id_uuid", "skills_owner_user_id_fkey", True),
            ("tools", "owner_user_id", "owner_user_id_uuid", "tools_owner_user_id_fkey", True),
            ("conversations", "user_id", "user_id_uuid", "conversations_user_id_fkey", False),
            ("job_runs", "user_id", "user_id_uuid", "job_runs_user_id_fkey", False),
            ("audit_logs", "user_id", "user_id_uuid", "audit_logs_user_id_fkey", False),
        ]:
            if table_name not in existing_tables:
                continue
            connection.execute(text(f"ALTER TABLE {table_name} DROP COLUMN IF EXISTS {old_column}"))
            connection.execute(text(f"ALTER TABLE {table_name} RENAME COLUMN {new_column} TO {old_column}"))
            connection.execute(
                text(
                    f"""
                    ALTER TABLE {table_name}
                    ADD CONSTRAINT {fk_name}
                    FOREIGN KEY ({old_column}) REFERENCES users(id)
                    """
                )
            )
            if needs_index:
                connection.execute(text(f"CREATE INDEX IF NOT EXISTS ix_{table_name}_{old_column} ON {table_name} ({old_column})"))

        if "messages" in existing_tables:
            connection.execute(text("ALTER TABLE messages DROP COLUMN IF EXISTS sender_id"))
            connection.execute(text("ALTER TABLE messages RENAME COLUMN sender_id_uuid TO sender_id"))


def migrate_user_storage_paths(connection) -> None:
    settings = get_settings()
    users_root = settings.resolved_users_root
    rows = connection.execute(text("SELECT id, id_uuid FROM users")).all()

    for legacy_id, uuid_value in rows:
        legacy_root = users_root / str(legacy_id)
        target_root = users_root / str(uuid_value)
        if legacy_root.exists() and not target_root.exists():
            target_root.parent.mkdir(parents=True, exist_ok=True)
            legacy_root.rename(target_root)
        _rewrite_asset_paths(connection, legacy_root, target_root)


def _rewrite_asset_paths(connection, legacy_root: Path, target_root: Path) -> None:
    legacy_prefix = str(legacy_root)
    target_prefix = str(target_root)
    if legacy_prefix == target_prefix:
        return

    for table_name in ["agents", "skills", "tools"]:
        connection.execute(
            text(
                f"""
                UPDATE {table_name}
                SET file_path = REPLACE(file_path, :legacy_prefix, :target_prefix)
                WHERE file_path LIKE :legacy_like
                """
            ),
            {
                "legacy_prefix": legacy_prefix,
                "target_prefix": target_prefix,
                "legacy_like": f"{legacy_prefix}%",
            },
        )


def seed_default_admin() -> None:
    settings = get_settings()
    with Session(engine) as session:
        existing = session.scalar(select(User).where(User.username == settings.bootstrap_admin_username))
        if existing is not None:
            return
        admin = User(
            username=settings.bootstrap_admin_username,
            password_hash=hash_password(settings.bootstrap_admin_password),
            status="active",
        )
        session.add(admin)
        session.commit()


def normalize_asset_storage_paths() -> None:
    with Session(engine) as session:
        bootstrap = UserAssetBootstrapService(session)
        user_ids = {
            *session.scalars(select(Agent.owner_user_id)).all(),
            *session.scalars(select(Skill.owner_user_id)).all(),
            *session.scalars(select(Tool.owner_user_id)).all(),
        }
        for user_id in user_ids:
            bootstrap.ensure_user_assets(user_id)
            bootstrap.normalize_user_asset_paths(user_id)
