from enum import Enum

from sqlalchemy.types import VARCHAR, TypeDecorator


class EnumString(TypeDecorator):  # type: ignore
    """Provide a way to have a kind of enum.

    This is better than using the database's ENUM type, because you have to do
    a migration every single time you change the enum.
    """

    impl = VARCHAR

    def __init__(self, enum_class, *arg, **kw):  # type: ignore
        TypeDecorator.__init__(self, *arg, **kw)
        if not issubclass(enum_class, Enum):  # nocov
            raise TypeError(
                "enum_class must be an subclass of Enum, got %s instead"
                % type(enum_class)
            )
        self.enum_class = enum_class

    def load_dialect_impl(self, dialect):  # type: ignore
        return dialect.type_descriptor(VARCHAR(50))

    def process_bind_param(self, value, dialect):  # type: ignore
        if value is None:  # nocov
            return value
        return value.value

    def process_result_value(self, value, dialect):  # type: ignore
        if value is None:  # nocov
            return value
        return self.enum_class(value)
