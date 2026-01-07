"""
Application entrypoint for local development and deployments.

For production environments, prefer running the app using a process
manager such as Gunicorn with Uvicorn workers.
"""
import os
import uvicorn

def main() -> None:
    """
    Launch the FastAPI application using Unvicorn.
    Configuration is driven via env variables.
    """
    uvicorn.run(
        app="src.VideoSharingApp.app:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("APPLICATION_RELOAD", "false").lower().strip() == "true",
    )

    return None


if __name__ == "__main__":
    main()
