import uuid
import warnings

from pydantic import BaseModel
from fastapi_users import schemas

class PostCreate(BaseModel):
    """
    DEPRICATED: Schema used when creating a new post.
    """
    title: str
    content: str

    def __init__(self, **data):
        warnings.warn(
            "PostCreate is deprecated.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(**data)


class PostResponse(BaseModel):
    """
    DEPRICATED: Schema returned to clients when fetching posts.
    """
    title: str
    content: str

    def __init__(self, **data):
        warnings.warn(
            "PostResponse is deprecated.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(**data)


class UserRead(schemas.BaseUser[uuid.UUID]):
    """
    Schema returned when reading user data.
    """
    pass


class UserCreate(schemas.BaseUserCreate):
    """
    Schema used during user registration.
    """
    pass


class UserUpdate(schemas.BaseUserUpdate):
    """
    Schema used when updating user profile.
    """
    pass
