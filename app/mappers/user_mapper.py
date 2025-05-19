from functools import lru_cache

from app.dto.users import UserResponse
from app.models import User


class UserMapper:
    async def user_to_response(self, user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            profile_picture=user.profile_picture,
            created_at=user.created_at
        )



@lru_cache()
def get_user_mapper():
    return UserMapper()