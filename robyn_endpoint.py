from robyn import Robyn
import time
import uuid
import orjson
from starlette.responses import Response

app = Robyn(__file__)

@app.post("/chat/completions")
async def chat_completions(request):
    start_time = time.time()
    body = orjson.loads(request.body)
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

    return Response(content=orjson.dumps(response_data), headers=headers, media_type="application/json")


app.start(port=8000)