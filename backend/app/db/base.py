from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all ORM models here so Alembic's autogenerate discovers them
# via Base.metadata. Order does not matter for discovery, but foreign key
# targets (users) must be importable before tables that reference them.
from app.users.infrastructure import orm_models as _users_orm  # noqa: F401, E402
from app.rooms.infrastructure import orm_models as _rooms_orm  # noqa: F401, E402
from app.combat.infrastructure import orm_models as _combat_orm  # noqa: F401, E402
from app.campaigns.infrastructure import orm_models as _campaigns_orm  # noqa: F401, E402
