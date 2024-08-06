from fastapi import FastAPI
from api.v1 import router as api_router
from mangum import Mangum

app = FastAPI()
app.include_router(api_router, prefix="/api/v1")
handler = Mangum(app)