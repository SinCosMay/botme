from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ready"}


@router.get("/metrics")
def metrics(request: Request) -> dict[str, float | int]:
    metrics_state = getattr(request.app.state, "metrics", {})
    return {
        "requests_total": int(metrics_state.get("requests_total", 0)),
        "requests_error_total": int(metrics_state.get("requests_error_total", 0)),
        "request_duration_ms_sum": float(metrics_state.get("request_duration_ms_sum", 0.0)),
        "request_duration_ms_avg": float(metrics_state.get("request_duration_ms_avg", 0.0)),
        "path_bucket_count": int(len(metrics_state.get("path_counts", {}))),
    }
