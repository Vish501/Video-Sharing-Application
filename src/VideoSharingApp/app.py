from fastapi import FastAPI

app_client = FastAPI()

@app_client.get("/hello-world")
def hello_world() -> dict[str, str]:
    return {"message": "Hello World!"}

