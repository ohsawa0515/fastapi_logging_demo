import sys
import time
import datetime
import json
import traceback
import asyncio
from typing import Callable, Optional
from logging import getLogger, StreamHandler, DEBUG
from fastapi import Request, Response
from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_504_GATEWAY_TIMEOUT

TIMEOUT = 10

logger = getLogger(__name__)
handler = StreamHandler(sys.stdout)
handler.setLevel(DEBUG)
logger.addHandler(handler)
logger.setLevel(DEBUG)


class LoggingContextRoute(APIRoute):

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            response = None
            record = {}
            await self._logging_request(request, record)

            # 処理にかかる時間を計測
            before = time.time()
            try:
                response = await self._execute_request(
                    request, original_route_handler, record)
            finally:
                duration = round(time.time() - before, 4)
                time_local = datetime.datetime.fromtimestamp(before)
                record["time_local"] = time_local.strftime(
                    "%Y/%m/%d %H:%M:%S%Z")
                record["request_time"] = str(duration)
                await self._logging_response(response, record)
                logger.info(json.dumps(record))

            return response

        return custom_route_handler

    async def _execute_request(
            self, request: Request,
            route_handler: Callable, record: dict) -> Response:
        try:
            response: Response = await self._wait_for_request(request, route_handler)
        except StarletteHTTPException as exc:
            record["error"] = exc.detail
            record["status"] = exc.status_code
            record["traceback"] = traceback.format_exc().splitlines()
            raise
        except RequestValidationError as exc:
            record["error"] = exc.errors()
            record["traceback"] = traceback.format_exc().splitlines()
            raise
        return response

    async def _wait_for_request(self, request: Request,
                                route_handler: Callable) -> Response:
        try:
            return await asyncio.wait_for(route_handler(request), timeout=TIMEOUT)
        except asyncio.TimeoutError:
            raise StarletteHTTPException(status_code=HTTP_504_GATEWAY_TIMEOUT,
                                         detail='Request processing time excedeed limit')

    async def _logging_response(
            self, response: Response, record: dict) -> Optional[Response]:
        if response is None:
            return
        try:
            record["response_body"] = json.loads(response.body.decode("utf-8"))
        except json.JSONDecodeError:
            record["response_body"] = response.body.decode("utf-8")
        record["status"] = response.status_code
        record["response_headers"] = {
            k.decode("utf-8"):
            v.decode("utf-8") for (k, v) in response.headers.raw
        }

    async def _logging_request(
            self, request: Request, record: dict) -> Optional[Response]:
        if await request.body():
            try:
                record["request_body"] = await request.json()
            except json.JSONDecodeError:
                record["request_body"] = (await request.body()).decode("utf-8")
        record["request_headers"] = {
            k.decode("utf-8"):
            v.decode("utf-8") for (k, v) in request.headers.raw
        }
        record["remote_addr"] = request.client.host
        record["request_uri"] = request.url.path
        record["request_method"] = request.method
