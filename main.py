from fastapi import FastAPI

from stepik.routers import categories, products, notes


# Создаём приложение FastAPI
app = FastAPI(
    title="FastAPI Интернет-магазин",
    version="0.1.0",
)

# Подключаем маршруты категорий
app.include_router(categories.router)
app.include_router(products.router)
# app.include_router(notes.router)


# Корневой эндпоинт для проверки
@app.get("/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Добро пожаловать в API интернет-магазина!"}