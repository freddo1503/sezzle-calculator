"""The HTTP layer. It validates, delegates and maps domain errors.

It never computes: the arithmetic lives in `app.engine`, which knows nothing
about HTTP. See .claude/rules/principles.md.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Calculator API",
    version="1.0.0",
    summary="Exact decimal arithmetic over HTTP.",
    root_path="/api",
)
