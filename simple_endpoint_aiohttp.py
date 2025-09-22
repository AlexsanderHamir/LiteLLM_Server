import time
import uuid
import orjson
from aiohttp import web


async def chat_completions(request: web.Request) -> web.Response:
    start_time = time.time()
    body_bytes = await request.read()
    body = orjson.loads(body_bytes or b"{}")
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
                    "content": f"Mock response for user {user} with {len(messages)} messages",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        },
    }

    headers = {
        "x-litellm-overhead-duration-ms": str(overhead_duration_ms),
        "content-type": "application/json",
    }

    return web.Response(
        body=orjson.dumps(response_data), status=200, headers=headers
    )


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_post("/chat/completions", chat_completions)
    return app


if __name__ == "__main__":
    web.run_app(create_app(), host="0.0.0.0", port=8000)


