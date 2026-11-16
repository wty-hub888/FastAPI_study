"""
FastAPI 学习笔记：请求体参数 + Field 校验 + 响应类型 + response_model + 异常处理

对应课程：黑马程序员 FastAPI（P8 请求体参数 ~ P14 异常处理）

运行方式（二选一）：
    1. PyCharm 里直接右键运行本文件（推荐，文件末尾有 uvicorn 启动代码）
    2. 终端执行：uvicorn 请求体与响应_study:app --reload
       （模块名 = 文件名去掉 .py，所以文件名用了下划线而不是连字符）

启动后访问：
    http://127.0.0.1:8000/docs      Swagger 交互式文档，可直接点 "Try it out" 测接口
    http://127.0.0.1:8000/redoc     另一种风格的文档
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import (
    HTMLResponse,
    PlainTextResponse,
    FileResponse,
    StreamingResponse,
    RedirectResponse,
)
from pydantic import BaseModel, Field

# 创建 FastAPI 实例
app = FastAPI(title="FastAPI 请求体与响应 Demo")


# ==================================================================
# 〇、基础路由：确认服务和文档都正常
# ==================================================================
@app.get("/")
async def root():
    return {"message": "Hello World"}


# ==================================================================
# 一、请求体参数（Request Body）
# ==================================================================
"""
请求体参数的作用：
    创建、更新资源 —— 一般配合 POST（新增）、PUT / PATCH（修改）使用
    数据放在 HTTP 请求的消息体里（通常是 JSON），适合传递大量、复杂的数据

定义步骤：
    1. 定义类型：继承 pydantic 的 BaseModel 写一个数据模型
    2. 类型注解：把视图函数的参数标注成该模型，FastAPI 就会自动
       从请求体里读取 JSON、按模型校验，再转成 Python 对象
"""


class User(BaseModel):
    """
    请求体模型
    - 字段类型就是最简单的校验：username 和 password 都必须是字符串
    - 两个字段都没写默认值，因此都是必填
    """
    username: str
    password: str


@app.post("/register")
async def register(user: User):
    """
    注册接口：接收 JSON 请求体

    - 参数 user 的类型是 User（Pydantic 模型）→ FastAPI 认定它是请求体参数
    - 请求体格式：{"username": "张三", "password": "123456"}
    - 返回的 user 是 Pydantic 模型对象，FastAPI 会把它自动序列化成 JSON
    """
    return user


# ==================================================================
# 二、类型注解 Field：给字段加校验规则和文档说明
# ==================================================================
"""
Field 参数速查：
    ...              必填（不写默认值也是必填，写 ... 更明确）
    gt / ge          大于 / 大于等于
    lt / le          小于 / 小于等于
    default          默认值
    description      字段描述（会显示在 /docs 文档里）
    min_length       最小长度
    max_length       最大长度

和 Path()、Query() 的用法是一致的，只是 Field() 用在请求体模型内部。
"""


class UserWithField(BaseModel):
    """
    同一个模型加上 Field 之后的效果：
    - username：有默认值 "张三"，不传也合法；长度必须在 2~10 之间
    - password：没有默认值 + 长度 3~20 → 必填，且长度不符合会返回 422
    """
    username: str = Field(
        default="张三",
        min_length=2,
        max_length=10,
        description="用户名，长度要求2-10个字",
    )
    password: str = Field(
        min_length=3,
        max_length=20,
        description="密码，长度要求3-20个字符",
    )


@app.post("/register-field")
async def register_with_field(user: UserWithField):
    """
    带 Field 校验的注册接口

    自测思路：
        - 传 {"password": "123"}                      → 成功，username 取默认值"张三"
        - 传 {"username": "张", "password": "123"}     → 422，username 长度不足 2
        - 传 {"username": "张三"}                      → 422，password 必填
    422 就是 FastAPI 自动做的请求参数校验失败响应。
    """
    return user


# ==================================================================
# 三、响应类型（Response）
# ==================================================================
"""
默认情况：FastAPI 会自动把视图函数返回的 Python 对象（字典、列表、Pydantic 模型等）
          经由 jsonable_encoder 转成 JSON 兼容格式，再包装成 JSONResponse 返回，
          省去了手动序列化的步骤。

需要返回非 JSON 数据（HTML、纯文本、文件、流）时，FastAPI 提供了多种响应类型：
    JSONResponse        默认响应，返回 JSON 数据
    HTMLResponse        返回 HTML 内容
    PlainTextResponse   返回纯文本
    FileResponse        返回文件下载 / 图片
    StreamingResponse   流式响应
    RedirectResponse    重定向

设置方式有两种：
    1. 装饰器中指定响应类：@app.get("/xx", response_class=HTMLResponse)
       → 适合"固定返回类型"的接口（HTML、纯文本等）
    2. 直接返回响应对象：return FileResponse(path)
       → 适合文件下载、图片、流式响应
"""


@app.get("/html", response_class=HTMLResponse)
async def get_html():
    """
    方式一：装饰器里指定 response_class
    返回的字符串会被当成 HTML 解析，浏览器直接渲染成一级标题
    """
    return "<h1>这是一级标题</h1>"


@app.get("/text", response_class=PlainTextResponse)
async def get_text():
    """对比 /html：同样返回字符串，这里按纯文本输出，标签不会被解析"""
    return "这是一段纯文本，<h1>不会</h1>被渲染"


@app.get("/file")
async def get_file():
    """
    方式二：直接返回响应对象
    在本机跑通需要项目里存在 files/1.jpeg（本目录已放好一张示例图）
    """
    path = "./files/1.jpeg"
    return FileResponse(path)


@app.get("/stream")
async def get_stream():
    """
    流式响应：视图函数返回生成器，数据分多次推给客户端
    适合大文件、实时日志、SSE 这类场景
    """

    def gen():
        for i in range(1, 6):
            yield f"第 {i} 条数据\n"

    return StreamingResponse(gen(), media_type="text/plain")


@app.get("/redirect")
async def do_redirect():
    """重定向：访问这个地址会被 307 跳到 /html"""
    return RedirectResponse("/html")


# ==================================================================
# 四、自定义响应数据格式：response_model
# ==================================================================
"""
response_model 是路径操作装饰器（@app.get / @app.post 等）的关键参数：
    用一个 Pydantic 模型严格定义、约束接口的输出格式
    好处：自动数据验证 + 序列化；模型未声明的字段会被过滤掉，
          这是保障数据安全的第一道防线（避免把内部字段泄露给前端）
"""


class News(BaseModel):
    """新闻响应模型：规定接口必须按 id、title、content 三个字段返回"""
    id: int
    title: str
    content: str


@app.get("/news/{id}", response_model=News)
async def get_news(id: int):
    """
    按 id 查询新闻

    - response_model=News → 响应体只保留 News 里声明过的字段
    - 下面故意多返了一个 internal_note，实际响应里不会出现
    """
    id_list = [1, 2, 3, 4, 5, 6]
    if id not in id_list:
        raise HTTPException(status_code=404, detail="当前id不存在")

    return {
        "id": id,
        "title": f"这是第{id}本书",
        "content": "这是一本好书",
        "internal_note": "这个字段模型里没声明，会被 response_model 过滤掉",
    }


# ==================================================================
# 五、异常处理：HTTPException
# ==================================================================
"""
对于客户端引发的错误（4xx，如资源未找到、认证失败）：
    用 fastapi.HTTPException 中断正常处理流程，返回标准错误响应

常用状态码：
    400 请求参数错误    401 未认证    403 无权限
    404 资源不存在      422 参数校验失败（FastAPI 自动返回）

响应格式固定为 {"detail": "你写的错误描述"}
"""


@app.get("/books/{id}")
async def get_book(id: int):
    """
    课程原始示例：id 不在列表里就抛 404
    raise 之后函数立刻中断，后面的 return 不会执行
    """
    id_list = [1, 2, 3, 4, 5, 6]
    if id not in id_list:
        raise HTTPException(status_code=404, detail="当前id不存在")

    return {"id": id}


# ==================================================================
# 启动入口（PyCharm 直接运行本文件即可）
# ==================================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
