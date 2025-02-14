from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from litestar import Litestar, post
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.dto.factory import dto_field

from .my_lib import Base


class User(Base):
    name: Mapped[str]
    password: Mapped[str] = mapped_column(info=dto_field("private"))
    created_at: Mapped[datetime] = mapped_column(info=dto_field("read-only"))


UserDTO = SQLAlchemyDTO[User]


@post("/users", dto=UserDTO, sync_to_thread=False)
def create_user(data: User) -> User:
    # even though the client sent the password and created_at field, it is not in the data object
    assert "password" not in vars(data)
    assert "created_at" not in vars(data)
    # normally the database would set the created_at timestamp
    data.created_at = datetime.min
    return data  # the response includes the created_at field


app = Litestar(route_handlers=[create_user])

# run: /users -H "Content-Type: application/json" -d '{"name":"Litestar User","password":"xyz","created_at":"2023-04-24T00:00:00Z"}'
