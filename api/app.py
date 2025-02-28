from sanic import Sanic, response
from sanic.log import logger
from sanic.request import Request
from sanic_cors import CORS
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from api.models import Base
from api.settings import SANIC_CONFIG

app = Sanic("CodingInterviewQuestionsApp")
app.config.update(SANIC_CONFIG)
CORS(app, resources={r"/*": {"origins": app.config.DOMAIN}})


@app.listener('before_server_start')
async def setup_db(_app, loop):
    _app.ctx.engine = create_async_engine(
        "postgresql+asyncpg://"
        f"{SANIC_CONFIG['DB_USER']}:{SANIC_CONFIG['DB_PASSWORD']}"
        f"@{SANIC_CONFIG['DB_HOST']}/{SANIC_CONFIG['DB_DATABASE']}",
        pool_size=5,
    )

    # Create tables on server startup
    async with _app.ctx.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.middleware("request")
async def on_request(request: Request) -> None:
    request.ctx.session = AsyncSession(request.app.ctx.engine, expire_on_commit=False)


@app.middleware("response")
async def on_response(request: Request, response) -> None:
    session = getattr(request.ctx, "session", None)
    if session:
        try:
            if response.status < 400:
                await session.commit()
            else:
                await session.rollback()
        except Exception as e:
            await session.rollback()
            logger.error("Session error: %s", e)
            raise
        finally:
            await session.close()


@app.listener('after_server_stop')
async def close_db(_app, loop):
    # Dispose engine on server shutdown
    await _app.ctx.engine.dispose()


@app.exception(Exception)
async def exception_handler(
    _request: Request, exception: Exception, **__
) -> response.HTTPResponse:
    """Exception handler returns error in json format."""
    status_code = getattr(exception, "status_code", 500)
    error = " ".join(str(arg) for arg in exception.args)

    if status_code == 500:
        logger.exception(exception)

    return response.json({"error": error}, status_code)
