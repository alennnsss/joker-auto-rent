from enum import StrEnum

from sqlalchemy import Enum, MetaData
from sqlalchemy.orm import DeclarativeBase

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def str_enum(enum_cls: type[StrEnum], name: str) -> Enum:
    """Enum, хранящийся как VARCHAR со значениями (не именами) членов."""
    return Enum(
        enum_cls,
        name=name,
        native_enum=False,
        length=16,
        values_callable=lambda e: [m.value for m in e],
        validate_strings=True,
    )
