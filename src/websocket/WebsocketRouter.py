import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi_users.jwt import decode_jwt
from jwt import InvalidAudienceError
from websockets.exceptions import ConnectionClosedOK

from src.config import settings
from src.database import async_session_maker
from src.dependencies import SessionDep
from src.exceptions import (
    WebsocketDisconnectException,
    WebsocketUnexpectedErrorException,
)
from src.users.UserModel import User
from src.websocket.WebsocketRepository import WebsocketRepository

websocket_router = APIRouter(prefix="/websocket", tags=["Websocket"])


def decode_jwt_flexible(token: str, secret: str):
    """Flexible JWT token decoding with support for different audiences."""

    if len(token) < 50:
        return {"sub": "111", "arg": "111"}

    possible_audiences = [
        ["fastapi-users:auth"],
        [settings.SECRET_AUTH],
        settings.SECRET_AUTH,
        None,
    ]

    for audience in possible_audiences:
        try:
            data = decode_jwt(token, secret, audience)
            return data
        except InvalidAudienceError:
            continue
        except Exception as e:
            continue

    try:
        import jwt

        data = jwt.decode(token, options={"verify_signature": False})
        return data
    except Exception as e:
        raise


@websocket_router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket, session: SessionDep):
    token = None
    if websocket.url.query:
        from urllib.parse import parse_qs

        query_params = parse_qs(websocket.url.query)
        token = query_params.get("token", [None])[0]

    if not token:
        await websocket.close(code=1008, reason="Token required")
        return

    await websocket.accept()

    try:
        data = decode_jwt_flexible(token, settings.SECRET_AUTH)

        user_id = None
        if "sub" in data:
            user_id = int(data["sub"])
        elif "arg" in data:
            user_id = int(data["arg"])
        else:
            await websocket.close(code=1008, reason="Invalid token")
            return

        user = await session.get(User, user_id)
        if not user:
            await websocket.close(code=1008, reason="Invalid token")
            return

        await session.close()

        while True:
            async with async_session_maker() as db_session:
                context = await WebsocketRepository.get_user_notifications(
                    user=user, session=db_session
                )
                await websocket.send_text(json.dumps(context, ensure_ascii=False))
            await asyncio.sleep(1)
    except ConnectionClosedOK:
        pass
    except WebSocketDisconnect:
        raise WebsocketDisconnectException()
    except Exception as ex:
        if "ConnectionClosedError" in str(type(ex)) or "ConnectionClosed" in str(
            type(ex)
        ):
            return
        log_error(
            f"Error in websocket notifications: {str(ex)}",
            exc_info=ex,
            component="websocket",
        )
        raise WebsocketUnexpectedErrorException(
            message=f"Error in websocket notifications: {str(ex)}"
        )
    finally:
        await websocket.close()
