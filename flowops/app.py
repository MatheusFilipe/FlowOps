from fastapi import FastAPI

from flowops.routers import ingredients, products

app = FastAPI()
app.include_router(ingredients.router)
app.include_router(products.router)
