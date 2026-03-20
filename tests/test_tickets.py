import pytest
from unittest.mock import AsyncMock, patch


async def _create_session_with_seats(auth_client):
    """Helper: cria movie + room + session e retorna (session_id, seat_id)."""
    movie = await auth_client.post("/movies/", json={
        "title": "Ticket Movie", "duration_minutes": 120
    })
    room = await auth_client.post("/rooms/", json={
        "name": "Sala Ticket", "rows": 1, "seats_per_row": 5
    })
    session = await auth_client.post("/sessions/", json={
        "movie_id": movie.json()["id"],
        "room_id": room.json()["id"],
        "starts_at": "2026-12-01T19:00:00",
    })

    with patch("app.services.seat_map.aioredis.from_url") as mock_redis:
        mock_instance = AsyncMock()
        mock_instance.exists = AsyncMock(return_value=False)
        mock_instance.aclose = AsyncMock()
        mock_redis.return_value = mock_instance
        seat_map = await auth_client.get(f"/sessions/{session.json()['id']}/seats")

    seat_id = seat_map.json()["seats"][0]["seat_id"]
    return session.json()["id"], seat_id


@pytest.mark.asyncio
async def test_checkout_success(auth_client):
    session_id, seat_id = await _create_session_with_seats(auth_client)

    # Reserva
    with patch("app.services.reservation.aioredis.from_url") as mock_redis:
        mock_instance = AsyncMock()
        mock_instance.set = AsyncMock(return_value=True)
        mock_instance.aclose = AsyncMock()
        mock_redis.return_value = mock_instance
        await auth_client.post("/reservations/", json={
            "session_id": session_id, "seat_id": seat_id,
        })

    # Checkout
    with patch("app.services.ticket.aioredis.from_url") as mock_redis:
        mock_instance = AsyncMock()
        mock_instance.get = AsyncMock(return_value=b"1")
        mock_instance.delete = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_redis.return_value = mock_instance

        response = await auth_client.post("/tickets/checkout", json={
            "session_id": session_id, "seat_id": seat_id,
        })
    assert response.status_code == 201
    data = response.json()
    assert "code" in data
    assert data["session_id"] == session_id
    assert data["seat_id"] == seat_id
    assert data["movie_title"] == "Ticket Movie"
    assert data["room_name"] == "Sala Ticket"


@pytest.mark.asyncio
async def test_checkout_without_reservation(auth_client):
    session_id, seat_id = await _create_session_with_seats(auth_client)

    # Tenta checkout sem reserva (Redis retorna None)
    with patch("app.services.ticket.aioredis.from_url") as mock_redis:
        mock_instance = AsyncMock()
        mock_instance.get = AsyncMock(return_value=None)
        mock_instance.aclose = AsyncMock()
        mock_redis.return_value = mock_instance

        response = await auth_client.post("/tickets/checkout", json={
            "session_id": session_id, "seat_id": seat_id,
        })
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_checkout_duplicate_seat(auth_client):
    """Tenta comprar o mesmo assento duas vezes."""
    session_id, seat_id = await _create_session_with_seats(auth_client)

    # Primeira reserva + checkout
    with patch("app.services.reservation.aioredis.from_url") as mock_redis:
        mock_instance = AsyncMock()
        mock_instance.set = AsyncMock(return_value=True)
        mock_instance.aclose = AsyncMock()
        mock_redis.return_value = mock_instance
        await auth_client.post("/reservations/", json={
            "session_id": session_id, "seat_id": seat_id,
        })

    with patch("app.services.ticket.aioredis.from_url") as mock_redis:
        mock_instance = AsyncMock()
        mock_instance.get = AsyncMock(return_value=b"1")
        mock_instance.delete = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_redis.return_value = mock_instance
        await auth_client.post("/tickets/checkout", json={
            "session_id": session_id, "seat_id": seat_id,
        })

    # Segunda tentativa — assento já comprado
    with patch("app.services.ticket.aioredis.from_url") as mock_redis:
        mock_instance = AsyncMock()
        mock_instance.get = AsyncMock(return_value=b"1")
        mock_instance.aclose = AsyncMock()
        mock_redis.return_value = mock_instance
        response = await auth_client.post("/tickets/checkout", json={
            "session_id": session_id, "seat_id": seat_id,
        })
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_my_tickets(auth_client):
    session_id, seat_id = await _create_session_with_seats(auth_client)

    # Reserva + checkout
    with patch("app.services.reservation.aioredis.from_url") as mock_redis:
        mock_instance = AsyncMock()
        mock_instance.set = AsyncMock(return_value=True)
        mock_instance.aclose = AsyncMock()
        mock_redis.return_value = mock_instance
        await auth_client.post("/reservations/", json={
            "session_id": session_id, "seat_id": seat_id,
        })

    with patch("app.services.ticket.aioredis.from_url") as mock_redis:
        mock_instance = AsyncMock()
        mock_instance.get = AsyncMock(return_value=b"1")
        mock_instance.delete = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_redis.return_value = mock_instance
        await auth_client.post("/tickets/checkout", json={
            "session_id": session_id, "seat_id": seat_id,
        })

    # Lista tickets
    response = await auth_client.get("/tickets/me")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["movie_title"] == "Ticket Movie"


@pytest.mark.asyncio
async def test_my_tickets_empty(auth_client):
    response = await auth_client.get("/tickets/me")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []
