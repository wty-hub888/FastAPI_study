from fastapi import FastAPI

# 创建 FastAPI 实例
app = FastAPI()

# 路由定义
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello")
async def get_hello():
    return {"msg": "Hello FastAPI"}

@app.get("/book/{id}")
async def get_book(id: str):
    return {"book_id": id,"title": f"Book {id}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
