import time
import uuid
import orjson
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route
import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve

async def chat_completions(request: Request):
    start_time = time.time()
    body = orjson.loads(await request.body())
    messages = body.get("messages", [])
    user = body.get("user", "anonymous")
    end_time = time.time()
    overhead_duration_ms = (end_time - start_time) * 1000

    response_data = {
        "id": f"chatcmpl-{uuid.uuid4()}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": body.get("model", "mock-model"),
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"Mock response for user {user} with {len(messages)} messages"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }

    headers = {
        "x-litellm-overhead-duration-ms": str(overhead_duration_ms),
        "content-type": "application/json"
    }

    return JSONResponse(content=response_data, headers=headers)

routes = [
    Route("/chat/completions", chat_completions, methods=["POST"]),
]

app = Starlette(debug=False, routes=routes)

if __name__ == "__main__":
    config = Config()
    config.bind = ["0.0.0.0:8000"]
    config.workers = 17               # high parallelism
    config.loop = "uvloop"            # fast C-based event loop
    config.worker_class = "uvloop"    # Hypercorn supports uvloop for async speed
    config.keep_alive_timeout = 1     # minimal keep-alive for HFT-like workloads
    config.backlog = 2048             # socket backlog for bursts

    asyncio.run(serve(app, config))
