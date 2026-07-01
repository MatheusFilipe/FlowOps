from fastapi import FastAPI

from flowops.routers import ingredients, orders, products, users

app = FastAPI()
app.include_router(ingredients.router)
app.include_router(orders.router)
app.include_router(products.router)
app.include_router(users.router)
