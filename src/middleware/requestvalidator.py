from starlette.middleware.base import BaseHTTPMiddleware
import time


class ValidateRequestMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, header_value="Example"):
        super().__init__(app)
        self.header_value = header_value

    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["Custom"] = self.header_value
        response.headers["X-Process-Time"] = str(process_time)
        # TODO: Add request validation logic here

        return response
