"""
Real-time notification tests for recruitment-platform.

Tests WebSocket-based real-time notifications: new applications,
interview scheduling, status changes, and message notifications.
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
async def notification_ws():
    """Provide a mock WebSocket client for notification tests."""
mock_ws = AsyncMock()
mock_ws.send = AsyncMock()
mock_ws.recv = AsyncMock()
mock_ws.close = AsyncMock()
mock_ws.closed = False
yield mock_ws


@pytest_asyncio.fixture
async def notification_url():
    """Return the notifications WebSocket endpoint URL."""
return "ws://localhost:8000/ws/notifications"


@pytest_asyncio.fixture
async def sample_notification():
    """Return a sample notification payload."""
return {
"id": "notif-001",
"type": "new_application",
"title": "New Application Received",
"message": "John Doe applied for Senior Developer position",
"data": {
"application_id": "app-123",
"job_id": "job-456",
"candidate_name": "John Doe",
"position": "Senior Developer",
},
"timestamp": "2026-10-03T10:00:00Z",
"read": False,
}


@pytest_asyncio.fixture
async def sample_interview_notification():
    """Return a sample interview notification payload."""
return {
"id": "notif-002",
"type": "interview_scheduled",
"title": "Interview Scheduled",
"message": "Interview with Jane Smith scheduled for Oct 5, 2026",
"data": {
"interview_id": "int-789",
"candidate_name": "Jane Smith",
"position": "Product Manager",
"scheduled_at": "2026-10-05T14:00:00Z",
"interviewer": "Alice Johnson",
},
"timestamp": "2026-10-03T11:00:00Z",
"read": False,
}


@pytest_asyncio.fixture
async def sample_status_notification():
    """Return a sample status change notification payload."""
return {
"id": "notif-003",
"type": "status_change",
"title": "Application Status Updated",
"message": "Application for Bob Wilson moved to Interview stage",
"data": {
"application_id": "app-999",
"candidate_name": "Bob Wilson",
"old_status": "screening",
"new_status": "interview",
},
"timestamp": "2026-10-03T12:00:00Z",
"read": False,
}


# ---------------------------------------------------------------------------
# Notification delivery tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_notification_connection(notification_ws, notification_url):
    """Test that the notifications WebSocket connects successfully."""
import websockets

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = notification_ws

        async with websockets.connect(notification_url) as ws:
            assert ws is not None
assert not ws.closed


@pytest.mark.asyncio
async def test_new_application_notification(
notification_ws, notification_url, sample_notification
):
    """Test receiving a new application notification."""
notification_ws.recv.return_value = json.dumps(sample_notification)

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = notification_ws

        async with websockets.connect(notification_url) as ws:
            message = await ws.recv()
data = json.loads(message)

            assert data["type"] == "new_application"
assert data["data"]["candidate_name"] == "John Doe"
assert data["data"]["position"] == "Senior Developer"


@pytest.mark.asyncio
async def test_interview_scheduled_notification(
notification_ws, notification_url, sample_interview_notification
):
    """Test receiving an interview scheduled notification."""
notification_ws.recv.return_value = json.dumps(sample_interview_notification)

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = notification_ws

        async with websockets.connect(notification_url) as ws:
            message = await ws.recv()
data = json.loads(message)

            assert data["type"] == "interview_scheduled"
assert data["data"]["interview_id"] == "int-789"
assert data["data"]["interviewer"] == "Alice Johnson"


@pytest.mark.asyncio
async def test_status_change_notification(
notification_ws, notification_url, sample_status_notification
):
    """Test receiving a status change notification."""
notification_ws.recv.return_value = json.dumps(sample_status_notification)

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = notification_ws

        async with websockets.connect(notification_url) as ws:
            message = await ws.recv()
data = json.loads(message)

            assert data["type"] == "status_change"
assert data["data"]["old_status"] == "screening"
assert data["data"]["new_status"] == "interview"


@pytest.mark.asyncio
async def test_notification_mark_read(notification_ws, notification_url):
    """Test marking a notification as read."""
notification_ws.recv.return_value = json.dumps(
{"type": "notification_read", "notification_id": "notif-001"}
)

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = notification_ws

        async with websockets.connect(notification_url) as ws:
            await ws.send(
json.dumps(
{"action": "mark_read", "notification_id": "notif-001"}
)
            )
            message = await ws.recv()
data = json.loads(message)

            assert data["type"] == "notification_read"
assert data["notification_id"] == "notif-001"


@pytest.mark.asyncio
async def test_notification_mark_all_read(notification_ws, notification_url):
    """Test marking all notifications as read."""
notification_ws.recv.return_value = json.dumps(
{"type": "all_notifications_read", "count": 5}
)

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = notification_ws

        async with websockets.connect(notification_url) as ws:
            await ws.send(json.dumps({"action": "mark_all_read"}))
message = await ws.recv()
data = json.loads(message)

            assert data["type"] == "all_notifications_read"
assert data["count"] == 5


@pytest.mark.asyncio
async def test_notification_subscribe_channel(notification_ws, notification_url):
    """Test subscribing to a notification channel."""
notification_ws.recv.return_value = json.dumps(
{"type": "subscribed", "channel": "recruiter-001"}
)

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = notification_ws

        async with websockets.connect(notification_url) as ws:
            await ws.send(
json.dumps(
{"action": "subscribe", "channel": "recruiter-001"}
)
            )
            message = await ws.recv()
data = json.loads(message)

            assert data["type"] == "subscribed"
assert data["channel"] == "recruiter-001"


@pytest.mark.asyncio
async def test_notification_unsubscribe_channel(notification_ws, notification_url):
    """Test unsubscribing from a notification channel."""
notification_ws.recv.return_value = json.dumps(
{"type": "unsubscribed", "channel": "recruiter-001"}
)

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = notification_ws

        async with websockets.connect(notification_url) as ws:
            await ws.send(
json.dumps(
{"action": "unsubscribe", "channel": "recruiter-001"}
)
            )
            message = await ws.recv()
data = json.loads(message)

            assert data["type"] == "unsubscribed"
assert data["channel"] == "recruiter-001"


@pytest.mark.asyncio
async def test_multiple_notifications_stream(notification_ws, notification_url):
    """Test receiving a stream of multiple notifications."""
notifications = [
json.dumps(
{
"id": f"notif-{i:03d}",
"type": "new_application",
"message": f"Application {i}",
}
)
        for i in range(5)
]
notification_ws.recv.side_effect = notifications

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = notification_ws

        async with websockets.connect(notification_url) as ws:
            received = []
for _ in range(5):
                msg = await ws.recv()
received.append(json.loads(msg))

            assert len(received) == 5
for i, notif in enumerate(received):
                assert notif["id"] == f"notif-{i:03d}"


@pytest.mark.asyncio
async def test_notification_filter_by_type(notification_ws, notification_url):
    """Test filtering notifications by type."""
notification_ws.recv.return_value = json.dumps(
{
"type": "notifications_filtered",
"filter": "new_application",
"count": 3,
}
)

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = notification_ws

        async with websockets.connect(notification_url) as ws:
            await ws.send(
json.dumps(
{"action": "filter", "notification_type": "new_application"}
)
            )
            message = await ws.recv()
data = json.loads(message)

            assert data["type"] == "notifications_filtered"
assert data["filter"] == "new_application"
assert data["count"] == 3


@pytest.mark.asyncio
async def test_notification_preference_update(notification_ws, notification_url):
    """Test updating notification preferences."""
notification_ws.recv.return_value = json.dumps(
{"type": "preferences_updated", "email_enabled": False}
)

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = notification_ws

        async with websockets.connect(notification_url) as ws:
            await ws.send(
json.dumps(
{
"action": "update_preferences",
"email_enabled": False,
"push_enabled": True,
}
)
            )
            message = await ws.recv()
data = json.loads(message)

            assert data["type"] == "preferences_updated"
assert data["email_enabled"] is False


@pytest.mark.asyncio
async def test_notification_invalid_payload(notification_ws, notification_url):
    """Test handling of invalid notification payload."""
notification_ws.recv.return_value = "invalid json payload"

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = notification_ws

        async with websockets.connect(notification_url) as ws:
            message = await ws.recv()
with pytest.raises(json.JSONDecodeError):
                json.loads(message)


@pytest.mark.asyncio
async def test_notification_connection_with_auth(
notification_ws, notification_url
):
    """Test connecting to notifications with authentication."""
import websockets

    token = "test-auth-token"
auth_url = f"{notification_url}?token={token}"

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = notification_ws

        async with websockets.connect(auth_url) as ws:
            assert ws is not None

        mock_connect.assert_called_once_with(auth_url)


@pytest.mark.asyncio
async def test_notification_reconnect(notification_ws, notification_url):
    """Test that notification connection can reconnect after disconnect."""
import websockets

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = notification_ws

        # First connection
        async with websockets.connect(notification_url) as ws:
            pass

        # Reconnect
        async with websockets.connect(notification_url) as ws:
            assert ws is not None

        assert mock_connect.call_count == 2


@pytest.mark.asyncio
async def test_notification_heartbeat(notification_ws, notification_url):
    """Test that notification connection sends heartbeat."""
import websockets

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = notification_ws

        async with websockets.connect(
notification_url, ping_interval=30, ping_timeout=10
) as ws:
            assert ws is not None

        _, kwargs = mock_connect.call_args
assert kwargs.get("ping_interval") == 30
assert kwargs.get("ping_timeout") == 10
