from enum import Enum

class APIVersion(str, Enum):
    V1 = "v1"
    V2 = "v2"

class AuthPaths:
    """
    Centralized authentication route definations.

    This class prevents hard-coded auth paths from being scattered
    across the application and enables safe versioning.
    """
    AUTH_PREFIX = "auth"
    JWT_LOGIN = "jwt/login"
    JWT_REFRESH = "jwt/refresh"
    JWT_LOGOUT = "jwt/logout"
    USER = "users"
    VERIFY = "verify" # Unused for now, future component

    @classmethod
    def base_prefix(cls, version: APIVersion) -> str:
        return f"/api/{version.value}"

    @classmethod
    def router_prefix(cls, version: APIVersion) -> str:
        return f"{cls.base_prefix(version)}/{cls.AUTH_PREFIX}"
    
    @classmethod
    def user_prefix(cls, version: APIVersion) -> str:
        return f"{cls.base_prefix(version)}/{cls.USER}"

    @classmethod
    def token_url(cls, version: APIVersion) -> str:
        return f"{cls.router_prefix(version)}/{cls.JWT_LOGIN}"

    @classmethod
    def refresh_url(cls, version: APIVersion) -> str:
        return f"{cls.router_prefix(version)}/{cls.JWT_REFRESH}"
    