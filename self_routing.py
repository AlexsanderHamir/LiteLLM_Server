from itertools import cycle
import httpx
from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response
from starlette.requests import Request
from starlette.routing import Route

# List of backend worker URLs
WORKERS = [
    "http://127.0.0.1:4000/chat/completions",
    "http://127.0.0.1:4001/chat/completions",
    "http://127.0.0.1:4002/chat/completions",
    "http://127.0.0.1:4003/chat/completions",
]

# Create a cycle iterator for round-robin
worker_cycle = cycle(WORKERS)

async def proxy_chat_completions(request: Request):
    body = await request.body()
    headers = dict(request.headers)

    # Pick next worker
    worker_url = next(worker_cycle)

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(worker_url, content=body, headers=headers, timeout=1000)
            return Response(content=resp.content, status_code=resp.status_code, headers=resp.headers)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

routes = [
    Route("/chat/completions", proxy_chat_completions, methods=["POST"]),
]

app = Starlette(debug=True, routes=routes)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, loop="uvloop", http="httptools")
