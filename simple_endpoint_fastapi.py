from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import time
import uuid
import orjson

app = FastAPI()

@app.post("/chat/completions")
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


if __name__ == "__main__":
    uvicorn.run(
        "simple_endpoint:app",
        host="0.0.0.0",
        port=8000,
        workers=17,              # high number of workers for parallelism
        loop="uvloop",           # fast C-based event loop
        http="httptools",        # fast HTTP parser
    )
