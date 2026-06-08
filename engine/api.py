"""REST API (FastAPI) over the CDS engine.

Phase 4 of the engine (see docs/architecture.md). The same operations as the MCP
server, exposed as HTTP endpoints with OpenAPI docs, for non-agent callers.

FastAPI is an **optional** dependency (`pip install ".[api]"`). The app is built
by a lazy factory, so importing this module never requires FastAPI and the core
stays standard-library-only. Stateless: nothing is stored and no inputs are
logged; a *not-a-medical-device* disclaimer rides on every result. See
DISCLAIMER.md.

Run:
    uvicorn "engine.api:create_app" --factory
    # or
    python -m engine.api
"""

from __future__ import annotations

from typing import Any

from . import dispatch, registry

_DESCRIPTION = (
    "Deterministic, citation-backed clinical decision-support algorithms. "
    "Inputs are structured features (never raw clinical notes). Not a medical "
    "device; outputs are scores and recommendation bands, not diagnosis or "
    "treatment."
)


def create_app() -> Any:
    """Build and return the FastAPI application.

    Imports FastAPI lazily; requires `pip install ".[api]"`.
    """
    from fastapi import Body, FastAPI, HTTPException

    try:
        from importlib.metadata import version as _pkg_version
        _version = _pkg_version("autonomous-care-algorithms")
    except Exception:  # pragma: no cover - metadata may be unavailable
        _version = "0"

    app = FastAPI(
        title="autonomous-care-algorithms",
        description=_DESCRIPTION,
        version=_version,
    )

    def _require_known(condition: str) -> None:
        if condition not in registry.condition_keys():
            raise HTTPException(status_code=404,
                                detail=f"unknown condition '{condition}'")

    @app.get("/")
    def root() -> dict[str, Any]:
        return {
            "name": "autonomous-care-algorithms",
            "conditions": len(registry.condition_keys()),
            "disclaimer": registry.DISCLAIMER,
            "docs": "/docs",
        }

    @app.get("/conditions")
    def conditions() -> list[dict[str, Any]]:
        return registry.list_conditions()

    @app.get("/presentations")
    def presentations() -> list[str]:
        return dispatch.presentations()

    @app.get("/conditions/{condition}")
    def describe(condition: str) -> dict[str, Any]:
        _require_known(condition)
        return registry.describe(condition)

    @app.get("/conditions/{condition}/schema")
    def schema(condition: str) -> dict[str, Any]:
        _require_known(condition)
        return registry.get_schema(condition)

    @app.post("/conditions/{condition}/run")
    def run(condition: str, features: dict[str, Any] = Body(...)) -> dict[str, Any]:
        _require_known(condition)
        errors = registry.validate(condition, features)
        if errors:
            raise HTTPException(status_code=422, detail={
                "errors": errors,
                "missing_inputs": registry.missing_inputs(condition, features),
            })
        try:
            result = registry.run(condition, features)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        return {"result": result, "disclaimer": registry.DISCLAIMER}

    @app.post("/suggest")
    def suggest(body: dict[str, Any] = Body(...)) -> list[dict[str, Any]]:
        return dispatch.suggest(body.get("features", {}), body.get("presentation"))

    @app.post("/run-applicable")
    def run_applicable(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
        return dispatch.run_applicable(body.get("features", {}), body.get("presentation"))

    return app


def main() -> None:
    """Serve the API with uvicorn."""
    import uvicorn

    uvicorn.run(create_app(), host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
