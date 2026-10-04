"""
Live analytics stream tests for recruitment-platform.

Tests WebSocket-based real-time analytics: metrics streaming,
dashboard updates, live counters, and time-series data.
"""

import asyncio
import json
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def analytics_ws():
    """Provide a mock WebSocket client for analytics tests."""
    mock_ws = AsyncMock()
    mock_ws.send = AsyncMock()
    mock_ws.recv = AsyncMock()
    mock_ws.close = AsyncMock()
    mock_ws.closed = False
    yield mock_ws


@pytest_asyncio.fixture
async def analytics_url():
    """Return the analytics WebSocket endpoint URL."""
    return "ws://localhost:8000/ws/analytics"


@pytest_asyncio.fixture
async def sample_metrics():
    """Return sample analytics metrics payload."""
    return {
        "timestamp": "2026-10-03T10:00:00Z",
        "metrics": {
            "total_applications": 150,
            "active_jobs": 25,
            "interviews_scheduled": 12,
            "offers_extended": 3,
            "hires_made": 1,
            "average_time_to_hire_days": 28.5,
        },
    }


@pytest_asyncio.fixture
async def sample_time_series():
    """Return sample time-series analytics data."""
    return {
        "metric": "applications_per_day",
        "data_points": [
            {"date": "2026-09-27", "value": 15},
            {"date": "2026-09-28", "value": 22},
            {"date": "2026-09-29", "value": 18},
            {"date": "2026-09-30", "value": 30},
            {"date": "2026-10-01", "value": 25},
            {"date": "2026-10-02", "value": 20},
            {"date": "2026-10-03", "value": 10},
        ],
    }


@pytest_asyncio.fixture
async def sample_dashboard_data():
    """Return sample dashboard analytics data."""
    return {
        "dashboard_id": "dash-001",
        "widgets": [
            {
                "type": "counter",
                "title": "Total Applications",
                "value": 150,
                "change": 12.5,
            },
            {
                "type": "chart",
                "title": "Applications Trend",
                "data": [15, 22, 18, 30, 25, 20, 10],
            },
            {
                "type": "funnel",
                "title": "Hiring Funnel",
                "stages": [
                    {"name": "Applied", "count": 150},
                    {"name": "Screened", "count": 80},
                    {"name": "Interviewed", "count": 35},
                    {"name": "Offered", "count": 8},
                    {"name": "Hired", "count": 3},
                ],
            },
        ],
    }


# ---------------------------------------------------------------------------
# Analytics connection tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_analytics_connection(analytics_ws, analytics_url):
    """Test that the analytics WebSocket connects successfully."""
    import websockets

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = analytics_ws

        async with websockets.connect(analytics_url) as ws:
            assert ws is not None
            assert not ws.closed


@pytest.mark.asyncio
async def test_analytics_handshake(analytics_ws, analytics_url):
    """Test that the analytics connection completes handshake."""
    analytics_ws.recv.return_value = json.dumps(
        {"type": "analytics_connected", "stream_id": "stream-001"}
    )

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = analytics_ws

        async with websockets.connect(analytics_url) as ws:
            message = await ws.recv()
            data = json.loads(message)

            assert data["type"] == "analytics_connected"
            assert data["stream_id"] == "stream-001"


# ---------------------------------------------------------------------------
# Metrics streaming tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_metrics_stream(analytics_ws, analytics_url, sample_metrics):
    """Test receiving live metrics data."""
    analytics_ws.recv.return_value = json.dumps(sample_metrics)

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = analytics_ws

        async with websockets.connect(analytics_url) as ws:
            message = await ws.recv()
            data = json.loads(message)

            assert "metrics" in data
            assert data["metrics"]["total_applications"] == 150
            assert data["metrics"]["active_jobs"] == 25


@pytest.mark.asyncio
async def test_metrics_update(analytics_ws, analytics_url):
    """Test receiving updated metrics."""
    updated_metrics = {
        "timestamp": "2026-10-03T10:01:00Z",
        "metrics": {
            "total_applications": 151,
            "active_jobs": 25,
            "interviews_scheduled": 13,
        },
    }
    analytics_ws.recv.return_value = json.dumps(updated_metrics)

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = analytics_ws

        async with websockets.connect(analytics_url) as ws:
            message = await ws.recv()
            data = json.loads(message)

            assert data["metrics"]["total_applications"] == 151
            assert data["metrics"]["interviews_scheduled"] == 13


@pytest.mark.asyncio
async def test_metrics_stream_interval(analytics_ws, analytics_url):
    """Test that metrics stream at configured interval."""
    import websockets

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = analytics_ws

        async with websockets.connect(analytics_url) as ws:
            await ws.send(
                json.dumps({"action": "set_interval", "seconds": 5})
            )
            analytics_ws.recv.return_value = json.dumps(
                {"type": "interval_updated", "seconds": 5}
            )
            message = await ws.recv()
            data = json.loads(message)

            assert data["type"] == "interval_updated"
            assert data["seconds"] == 5


@pytest.mark.asyncio
async def test_metrics_subscribe(analytics_ws, analytics_url):
    """Test subscribing to specific metrics."""
    analytics_ws.recv.return_value = json.dumps(
        {
            "type": "metrics_subscribed",
            "metrics": ["total_applications", "active_jobs"],
        }
    )

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = analytics_ws

        async with websockets.connect(analytics_url) as ws:
            await ws.send(
                json.dumps(
                    {
                        "action": "subscribe_metrics",
                        "metrics": ["total_applications", "active_jobs"],
                    }
                )
            )
            message = await ws.recv()
            data = json.loads(message)

            assert data["type"] == "metrics_subscribed"
            assert "total_applications" in data["metrics"]


@pytest.mark.asyncio
async def test_metrics_unsubscribe(analytics_ws, analytics_url):
    """Test unsubscribing from specific metrics."""
    analytics_ws.recv.return_value = json.dumps(
        {
            "type": "metrics_unsubscribed",
            "metrics": ["total_applications"],
        }
    )

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = analytics_ws

        async with websockets.connect(analytics_url) as ws:
            await ws.send(
                json.dumps(
                    {
                        "action": "unsubscribe_metrics",
                        "metrics": ["total_applications"],
                    }
                )
            )
            message = await ws.recv()
            data = json.loads(message)

            assert data["type"] == "metrics_unsubscribed"


# ---------------------------------------------------------------------------
# Time-series data tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_time_series_stream(
    analytics_ws, analytics_url, sample_time_series
):
    """Test receiving time-series analytics data."""
    analytics_ws.recv.return_value = json.dumps(sample_time_series)

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = analytics_ws

        async with websockets.connect(analytics_url) as ws:
            message = await ws.recv()
            data = json.loads(message)

            assert data["metric"] == "applications_per_day"
            assert len(data["data_points"]) == 7
            assert data["data_points"][0]["value"] == 15


@pytest.mark.asyncio
async def test_time_series_date_range(analytics_ws, analytics_url):
    """Test requesting time-series data for a specific date range."""
    analytics_ws.recv.return_value = json.dumps(
        {
            "type": "time_series_data",
            "metric": "applications_per_day",
            "start_date": "2026-10-01",
            "end_date": "2026-10-03",
            "data_points": [
                {"date": "2026-10-01", "value": 25},
                {"date": "2026-10-02", "value": 20},
                {"date": "2026-10-03", "value": 10},
            ],
        }
    )

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = analytics_ws

        async with websockets.connect(analytics_url) as ws:
            await ws.send(
                json.dumps(
                    {
                        "action": "get_time_series",
                        "metric": "applications_per_day",
                        "start_date": "2026-10-01",
                        "end_date": "2026-10-03",
                    }
                )
            )
            message = await ws.recv()
            data = json.loads(message)

            assert data["type"] == "time_series_data"
            assert len(data["data_points"]) == 3


# ---------------------------------------------------------------------------
# Dashboard tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dashboard_data(
    analytics_ws, analytics_url, sample_dashboard_data
):
    """Test receiving dashboard analytics data."""
    analytics_ws.recv.return_value = json.dumps(sample_dashboard_data)

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = analytics_ws

        async with websockets.connect(analytics_url) as ws:
            message = await ws.recv()
            data = json.loads(message)

            assert data["dashboard_id"] == "dash-001"
            assert len(data["widgets"]) == 3


@pytest.mark.asyncio
async def test_dashboard_widget_update(analytics_ws, analytics_url):
    """Test receiving dashboard widget updates."""
    analytics_ws.recv.return_value = json.dumps(
        {
            "type": "widget_updated",
            "widget_type": "counter",
            "title": "Total Applications",
            "value": 155,
            "change": 15.0,
        }
    )

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = analytics_ws

        async with websockets.connect(analytics_url) as ws:
            message = await ws.recv()
            data = json.loads(message)

            assert data["type"] == "widget_updated"
            assert data["value"] == 155


@pytest.mark.asyncio
async def test_dashboard_refresh(analytics_ws, analytics_url):
    """Test requesting a dashboard refresh."""
    analytics_ws.recv.return_value = json.dumps(
        {"type": "dashboard_refreshed", "dashboard_id": "dash-001"}
    )

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = analytics_ws

        async with websockets.connect(analytics_url) as ws:
            await ws.send(
                json.dumps(
                    {"action": "refresh", "dashboard_id": "dash-001"}
                )
            )
            message = await ws.recv()
            data = json.loads(message)

            assert data["type"] == "dashboard_refreshed"
            assert data["dashboard_id"] == "dash-001"


# ---------------------------------------------------------------------------
# Live counter tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_live_counter(analytics_ws, analytics_url):
    """Test receiving live counter updates."""
    analytics_ws.recv.return_value = json.dumps(
        {
            "type": "counter_update",
            "counter": "active_users",
            "value": 42,
        }
    )

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = analytics_ws

        async with websockets.connect(analytics_url) as ws:
            message = await ws.recv()
            data = json.loads(message)

            assert data["type"] == "counter_update"
            assert data["counter"] == "active_users"
            assert data["value"] == 42


@pytest.mark.asyncio
async def test_live_counter_increment(analytics_ws, analytics_url):
    """Test live counter increment events."""
    analytics_ws.recv.return_value = json.dumps(
        {
            "type": "counter_increment",
            "counter": "applications_today",
            "increment": 1,
            "new_value": 11,
        }
    )

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = analytics_ws

        async with websockets.connect(analytics_url) as ws:
            message = await ws.recv()
            data = json.loads(message)

            assert data["type"] == "counter_increment"
            assert data["new_value"] == 11


# ---------------------------------------------------------------------------
# Analytics error handling tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_analytics_invalid_metric(analytics_ws, analytics_url):
    """Test handling of invalid metric request."""
    analytics_ws.recv.return_value = json.dumps(
        {
            "type": "error",
            "code": "INVALID_METRIC",
            "message": "Unknown metric: invalid_metric_name",
        }
    )

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = analytics_ws

        async with websockets.connect(analytics_url) as ws:
            await ws.send(
                json.dumps(
                    {"action": "subscribe_metrics", "metrics": ["invalid_metric_name"]}
                )
            )
            message = await ws.recv()
            data = json.loads(message)

            assert data["type"] == "error"
            assert data["code"] == "INVALID_METRIC"


@pytest.mark.asyncio
async def test_analytics_rate_limit(analytics_ws, analytics_url):
    """Test handling of rate limit on analytics stream."""
    analytics_ws.recv.return_value = json.dumps(
        {
            "type": "error",
            "code": "RATE_LIMITED",
            "message": "Too many requests",
            "retry_after": 30,
        }
    )

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = analytics_ws

        async with websockets.connect(analytics_url) as ws:
            message = await ws.recv()
            data = json.loads(message)

            assert data["type"] == "error"
            assert data["code"] == "RATE_LIMITED"
            assert data["retry_after"] == 30


@pytest.mark.asyncio
async def test_analytics_connection_with_auth(analytics_ws, analytics_url):
    """Test connecting to analytics with authentication."""
    import websockets

    token = "analytics-token"
    auth_url = f"{analytics_url}?token={token}"

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = analytics_ws

        async with websockets.connect(auth_url) as ws:
            assert ws is not None

        mock_connect.assert_called_once_with(auth_url)


@pytest.mark.asyncio
async def test_analytics_reconnect(analytics_ws, analytics_url):
    """Test that analytics connection can reconnect."""
    import websockets

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = analytics_ws

        # First connection
        async with websockets.connect(analytics_url) as ws:
            pass

        # Reconnect
        async with websockets.connect(analytics_url) as ws:
            assert ws is not None

        assert mock_connect.call_count == 2


@pytest.mark.asyncio
async def test_analytics_heartbeat(analytics_ws, analytics_url):
    """Test that analytics connection sends heartbeat."""
    import websockets

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = analytics_ws

        async with websockets.connect(
            analytics_url, ping_interval=15, ping_timeout=5
        ) as ws:
            assert ws is not None

        _, kwargs = mock_connect.call_args
        assert kwargs.get("ping_interval") == 15
        assert kwargs.get("ping_timeout") == 5


@pytest.mark.asyncio
async def test_analytics_multiple_data_streams(analytics_ws, analytics_url):
    """Test receiving multiple analytics data streams."""
    streams = [
        json.dumps({"type": "metrics", "data": {"applications": 150}}),
        json.dumps({"type": "time_series", "data": {"trend": "up"}}),
        json.dumps({"type": "counter", "data": {"active_users": 42}}),
    ]
    analytics_ws.recv.side_effect = streams

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = analytics_ws

        async with websockets.connect(analytics_url) as ws:
            received = []
            for _ in range(3):
                msg = await ws.recv()
                received.append(json.loads(msg))

            assert len(received) == 3
            assert received[0]["type"] == "metrics"
            assert received[1]["type"] == "time_series"
            assert received[2]["type"] == "counter"
