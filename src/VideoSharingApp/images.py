import os
from dotenv import load_dotenv
from imagekitio import ImageKit
from functools import lru_cache

load_dotenv()

class ImageKitConfigError(RuntimeError):
    """
    Raised when ImageKit configuration is invalid. Helps in making logs more easily searchable.
    """
    pass


@lru_cache(maxsize=1) # Conserve memory
def create_imagekit_client() -> ImageKit:
    """
    Initializes an ImageKit client

    Returns:
    - ImageKit: singleton ImageKit client.

    Raises:
    - ImageKitConfigError: If required environment variables are missing.
    """
    private_key = os.environ.get("IMAGEKIT_PRIVATE_KEY")

    if not private_key:
        raise ImageKitConfigError("IMAGEKIT_PRIVATE_KEY is not set in environment variables.")
    
    try:
        return ImageKit(private_key=private_key)
    except Exception as e:
        raise ImageKitConfigError("Failded to initialize an ImageKit client") from e
        