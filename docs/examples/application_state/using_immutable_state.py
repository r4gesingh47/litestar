from litestar import Litestar, get
from litestar.datastructures import ImmutableState


@get("/", sync_to_thread=False)
def handler(state: ImmutableState) -> dict:
    setattr(state, "count", 1)  # raises AttributeError
    return state.dict()


app = Litestar(route_handlers=[handler])
