"""
Simple FastAPI endpoint for RPS testing with Locust
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time
import uuid

app = FastAPI()

@app.post("/chat/completions")
async def chat_completions(request: Request):
    """Mock chat completions endpoint that can handle Locust test"""
    start_time = time.time()
    
    # Get request body
    body = await request.json()
    
    # Extract message content for processing
    messages = body.get("messages", [])
    user = body.get("user", "anonymous")
    
    # Calculate overhead duration
    end_time = time.time()
    overhead_duration_ms = (end_time - start_time) * 1000
    
    # Mock response similar to OpenAI format
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
    
    # Add LiteLLM overhead header for your Locust test
    headers = {
        "x-litellm-overhead-duration-ms": str(overhead_duration_ms),
        "content-type": "application/json"
    }
    
    return JSONResponse(content=response_data, headers=headers)


# ---- Gunicorn programmatic runner ----
from gunicorn.app.base import BaseApplication
import multiprocessing

def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1  # Gunicorn formula

class StandaloneGunicornApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        cfg = getattr(self, "cfg", None)
        if cfg is None:
            return
        settings = getattr(cfg, "settings", {}) or {}
        config = {key: value for key, value in self.options.items()
                  if key in settings and value is not None}
        for key, value in config.items():
            cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == "__main__":
    options = {
    "bind": "0.0.0.0:8000",
    "workers": number_of_workers(),  # usually cores * 2 for I/O workloads
    "worker_class": "uvicorn.workers.UvicornWorker",
    "timeout": 30,
    
    # 🚀 performance knobs:
    "worker_connections": 2000,   # raise if lots of concurrent clients
    "keepalive": 1000,               
    "backlog": 2048,              # socket backlog queue
    "graceful_timeout": 15,       # how long workers have to finish on restart
    "max_requests": 0,            # set >0 if you see memory leaks
    "max_requests_jitter": 0,
}

    StandaloneGunicornApplication(app, options).run()
