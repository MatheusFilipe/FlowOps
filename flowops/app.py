from fastapi import FastAPI

from flowops.routers import ingredients

app = FastAPI()
app.include_router(ingredients.router)
