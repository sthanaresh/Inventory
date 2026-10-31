from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.categories import router as categories_router
from routers.products import router as products_router
app = FastAPI(title="Inventory Management API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(categories_router)
app.include_router(products_router)

