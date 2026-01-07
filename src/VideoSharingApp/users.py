import uuid
import os
from typing import Optional
from dotenv import load_dotenv

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase

from src.VideoSharingApp.database import User, get_user_db
from src.VideoSharingApp.utils.logger import get_logger
from src.VideoSharingApp.constants.auth import AuthPaths, APIVersion

load_dotenv()

logger = get_logger(__name__)
