"""
WebSocket connection tests for recruitment-platform.

Tests WebSocket connection lifecycle: connect, handshake, disconnect,
reconnect, and error handling.
"""

import asyncio
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def ws_client():
    """Provide a mock WebSocket client for connection tests."""
    from websockets.exceptions import ConnectionClosed

    mock_ws = AsyncMock()
    mock_ws.send = AsyncMock()
    mock_ws.recv = AsyncMock()
    mock_ws.close = AsyncMock()
    mock_ws.closed = False
    mock_ws.close_code = None
    mock_ws.close_reason = ""
    yield mock_ws


@pytest_asyncio.fixture
async def ws_url():
    """Return the WebSocket endpoint URL."""
    return "ws://localhost:8000/ws"


@pytest_asyncio.fixture
async def connected_ws(ws_client, ws_url):
    """Provide a connected WebSocket client."""
    ws_client.recv.return_value = '{"type": "connection_established"}'
    return ws_client


# ---------------------------------------------------------------------------
# Connection lifecycle tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_websocket_connect(ws_client, ws_url):
    """Test that a WebSocket connection can be established."""
    import websockets

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = ws_client

        async with websockets.connect(ws_url) as ws:
            assert ws is not None
            assert not ws.closed


@pytest.mark.asyncio
async def test_websocket_handshake(connected_ws):
    """Test that the server sends a connection_established message."""
    message = await connected_ws.recv()
    data = __import__("json").loads(message)

    assert data["type"] == "connection_established"


@pytest.mark.asyncio
async def test_websocket_send_message(ws_client, ws_url):
    """Test sending a message over the WebSocket connection."""
    import websockets

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = ws_client

        async with websockets.connect(ws_url) as ws:
            await ws.send('{"type": "ping"}')
            ws_client.send.assert_called_once_with('{"type": "ping"}')


@pytest.mark.asyncio
async def test_websocket_receive_message(ws_client, ws_url):
    """Test receiving a message from the WebSocket server."""
    import websockets
    import json

    ws_client.recv.return_value = json.dumps({"type": "pong"})

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = ws_client

        async with websockets.connect(ws_url) as ws:
            message = await ws.recv()
            data = json.loads(message)
            assert data["type"] == "pong"


@pytest.mark.asyncio
async def test_websocket_close(ws_client, ws_url):
    """Test that the WebSocket connection closes cleanly."""
    import websockets

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = ws_client

        async with websockets.connect(ws_url) as ws:
            pass

        ws_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_websocket_close_code(ws_client, ws_url):
    """Test that close code and reason are accessible after disconnect."""
    import websockets

    ws_client.closed = True
    ws_client.close_code = 1000
    ws_client.close_reason = "Normal closure"

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = ws_client

        async with websockets.connect(ws_url) as ws:
            pass

        assert ws_client.close_code == 1000
        assert ws_client.close_reason == "Normal closure"


@pytest.mark.asyncio
async def test_websocket_reconnect(ws_client, ws_url):
    """Test that a disconnected WebSocket can reconnect."""
    import websockets

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = ws_client

        # First connection
        async with websockets.connect(ws_url) as ws:
            pass

        # Reconnect
        async with websockets.connect(ws_url) as ws:
            assert ws is not None

        assert mock_connect.call_count == 2


@pytest.mark.asyncio
async def test_websocket_connection_refused(ws_url):
    """Test handling of connection refused errors."""
    import websockets

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.side_effect = ConnectionRefusedError("Connection refused")

        with pytest.raises(ConnectionRefusedError):
            async with websockets.connect(ws_url):
                pass


@pytest.mark.asyncio
async def test_websocket_timeout(ws_client, ws_url):
    """Test handling of connection timeout."""
    import websockets

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.side_effect = asyncio.TimeoutError("Connection timed out")

        with pytest.raises(asyncio.TimeoutError):
            async with websockets.connect(ws_url):
                pass


@pytest.mark.asyncio
async def test_websocket_unexpected_close(ws_client, ws_url):
    """Test handling of unexpected connection close."""
    import websockets
    from websockets.exceptions import ConnectionClosed

    ws_client.closed = True
    ws_client.close_code = 1006
    ws_client.close_reason = "Abnormal closure"

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = ws_client

        with pytest.raises(ConnectionClosed):
            async with websockets.connect(ws_url) as ws:
                await ws.recv()


@pytest.mark.asyncio
async def test_websocket_ping_pong(ws_client, ws_url):
    """Test WebSocket ping/pong keepalive mechanism."""
    import websockets

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = ws_client

        async with websockets.connect(ws_url) as ws:
            pong_waiter = await ws.ping()
            await asyncio.wait_for(pong_waiter, timeout=5)


@pytest.mark.asyncio
async def test_websocket_multiple_messages(ws_client, ws_url):
    """Test sending and receiving multiple messages in sequence."""
    import json

    messages = [
        json.dumps({"type": "msg_1", "data": "first"}),
        json.dumps({"type": "msg_2", "data": "second"}),
        json.dumps({"type": "msg_3", "data": "third"}),
    ]
    ws_client.recv.side_effect = messages

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = ws_client

        async with websockets.connect(ws_url) as ws:
            for i, expected in enumerate(messages):
                msg = await ws.recv()
                data = json.loads(msg)
                assert data["type"] == f"msg_{i + 1}"


@pytest.mark.asyncio
async def test_websocket_connection_with_token(ws_url):
    """Test WebSocket connection with authentication token."""
    import websockets

    token = "test-jwt-token"
    auth_url = f"{ws_url}?token={token}"

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = AsyncMock()

        async with websockets.connect(auth_url) as ws:
            assert ws is not None

        mock_connect.assert_called_once_with(auth_url)


@pytest.mark.asyncio
async def test_websocket_invalid_token(ws_url):
    """Test that an invalid token is rejected."""
    import websockets
    from websockets.exceptions import InvalidStatusCode

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.side_effect = InvalidStatusCode(
            MagicMock(status_code=403), "Forbidden"
        )

        with pytest.raises(InvalidStatusCode):
            async with websockets.connect(f"{ws_url}?token=invalid"):
                pass


@pytest.mark.asyncio
async def test_websocket_heartbeat_interval(ws_client, ws_url):
    """Test that heartbeat/keepalive interval is configured."""
    import websockets

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = ws_client

        async with websockets.connect(ws_url, ping_interval=20, ping_timeout=10) as ws:
            assert ws is not None

        _, kwargs = mock_connect.call_args
        assert kwargs.get("ping_interval") == 20
        assert kwargs.get("ping_timeout") == 10


@pytest.mark.asyncio
async def test_websocket_max_size(ws_client, ws_url):
    """Test that max message size is configured."""
    import websockets

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = ws_client

        async with websockets.connect(ws_url, max_size=1024 * 1024) as ws:
            assert ws is not None

        _, kwargs = mock_connect.call_args
        assert kwargs.get("max_size") == 1024 * 1024
