import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import uuid
import orjson
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route

# Thread pool shared by this process
thread_pool = ThreadPoolExecutor(max_workers=8)  # adjust based on CPU cores

def process_request(body: dict) -> dict:
    messages = body.get("messages", [])
    user = body.get("user", "anonymous")
    return {
        "id": f"chatcmpl-{uuid.uuid4()}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": body.get("model", "mock-model"),
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"Processed {len(messages)} messages for user {user}",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
    }

async def chat_completions(request: Request):
    body = orjson.loads(await request.body())
    loop = asyncio.get_running_loop()
    
    # Offload CPU-heavy work to thread pool and wait for result
    result = await loop.run_in_executor(thread_pool, process_request, body)
    
    # Return the processed result to the client
    return JSONResponse(content=result)

routes = [
    Route("/chat/completions", chat_completions, methods=["POST"]),
]

app = Starlette(debug=False, routes=routes)
