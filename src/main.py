from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.AuthRouter import auth_router
from src.config import settings
from src.notifications.NotificationRouter import notification_router
from src.organizations.OrganizationRouter import organization_router
from src.settings.SettingsRouter import settings_router
from src.users.UserRouter import router_user
from src.utils.managers.SMTP.tasks.router import SMTP_router
from src.websocket.WebsocketRouter import websocket_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield  # Important! This separates startup and shutdown logic


app = FastAPI(
    title="FastAPI Template Backend",
    description="Backend for FastAPI Template",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=settings.CORS_HEADERS,
)

app.include_router(auth_router, prefix="/api/v1/user", tags=["Auth"])
app.include_router(router_user, prefix="/api/v1/user", tags=["User"])
app.include_router(
    organization_router, prefix="/api/v1/organization", tags=["Organization"]
)


app.include_router(
    notification_router, prefix="/api/v1/notification", tags=["Notification"]
)
app.include_router(websocket_router, tags=["WebSocket"])
app.include_router(settings_router, prefix="/api/v1/settings", tags=["Setting"])

app.include_router(SMTP_router, prefix="/api/v1/smtp", tags=["SMTP"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
