# uvicorn main:app --reload --port 8000
# uvicorn main:app --reload --host 0.0.0.0 --port 8000

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# 允許 Flutter 前端跨域請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開發階段可用 "*"，正式環境請指定來源
    allow_methods=["*"],
    allow_headers=["*"],
)

class HelloRequest(BaseModel):
    name: str

@app.post("/hello")
def say_hello(req: HelloRequest):
    return {"message": f"Hello, {req.name}!"}
