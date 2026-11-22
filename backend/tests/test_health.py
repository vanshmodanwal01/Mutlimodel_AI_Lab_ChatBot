from backend.app.api.routes.health import health_check
from backend.app.db.session import get_session


def test_health_check_endpoint():
    db = get_session()
    result = health_check(db)
    assert result["status"] == "healthy"
    assert result["app_name"] == "MindBridge AI"
    assert result["database"]["status"] == "healthy"
    assert result["database"]["engine"] in ("mysql", "sqlite")
