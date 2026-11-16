# 导入依赖
from fastapi import FastAPI, Path, Query
from pydantic import BaseModel  # 请求体必须用Pydantic模型

# 创建FastAPI实例
app = FastAPI(title="FastAPI参数学习Demo")

# ---------------------- 1. 基础路由（HelloWorld） ----------------------
"""
路由：URL地址 和 处理函数 的映射关系
@app.get("/") 装饰器：
    app：FastAPI实例
    get：HTTP请求方法GET
    "/"：请求路径
async def root：异步处理函数
return：接口响应结果
"""
@app.get("/")
async def root():
    return {"message": "Hello World"}


# ---------------------- 2. 路径参数 Path ----------------------
"""
路径参数：属于URL路径的一部分，格式 /book/{id}
作用：定位唯一资源，一般用于GET查询单个资源
Path()：用来做参数校验、描述
    gt：大于，lt：小于
    ge：大于等于，le：小于等于
    min_length/max_length：字符串长度限制
    description：接口文档描述
    default=... 代表必填
"""
@app.get("/book/{id}")
async def get_book(
    id: int = Path(default=..., gt=0, lt=101, description="书籍id，取值范围1~100")
):
    return {"id": id, "title": f"这是第{id}本书"}


# 字符串类型路径参数，长度限制 2~10
@app.get("/author/{name}")
async def get_author(
    name: str = Path(default=..., min_length=2, max_length=10, description="作者名字，2-10个字符")
):
    return {"msg": f"这是{name}的信息"}


# ---------------------- 3. 查询参数 Query ----------------------
"""
查询参数：在URL ? 后面，格式 ?skip=0&limit=10
作用：对资源列表过滤、分页、排序
Query()：校验查询参数，和Path参数用法一致
"""
@app.get("/news/news_list")
async def get_news_list(
    skip: int = Query(default=0, lt=100, description="跳过的记录数，分页偏移量"),
    limit: int = Query(default=10, description="返回的记录条数")
):
    return {"skip": skip, "limit": limit}


# ---------------------- 4. 请求体参数 Body（POST） ----------------------
"""
请求体：放在HTTP请求消息体（body）里，一般是JSON
适用POST/PUT，适合传递大量、复杂数据
必须定义Pydantic的BaseModel类来接收json
"""
# 定义请求体模型
class BookBody(BaseModel):
    title: str       # 书名
    price: float     # 价格
    stock: int       # 库存

@app.post("/book")
async def create_book(book: BookBody):
    """新增图书，接收JSON请求体"""
    # book 就是前端传过来的json自动转成的对象
    return {
        "msg": "图书创建成功",
        "data": book
    }
