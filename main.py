import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app="src.VideoSharingApp.app:app_client", host="0.0.0.0", port=8000, reload=True
        )
    