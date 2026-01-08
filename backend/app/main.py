from fastapi import FastAPI, APIRouter
from app.api.api_v1.endpoints import decisions, documents, auth, test_endpoint
from app.core.config import settings

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, allow all. Improve for prod.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(test_endpoint.router, tags=["test"])
api_router.include_router(decisions.router, tags=["decisions"])
api_router.include_router(documents.router, tags=["documents"])

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Credit AI"}
