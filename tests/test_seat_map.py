import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_get_seat_map(auth_client):
    movie = await auth_client.post("/movies/", json={
        "title": "Test Movie", "duration_minutes": 120
    })
    room = await auth_client.post("/rooms/", json={
        "name": "Sala 1", "rows": 2, "seats_per_row": 3
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

        response = await auth_client.get(f"/sessions/{session.json()['id']}/seats")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session.json()["id"]
        assert data["room_name"] == "Sala 1"
        assert len(data["seats"]) == 6  # 2 rows * 3 seats
        # todos devem estar available
        for seat in data["seats"]:
            assert seat["status"] == "available"


@pytest.mark.asyncio
async def test_seat_map_session_not_found(client):
    with patch("app.services.seat_map.aioredis.from_url"):
        response = await client.get("/sessions/9999/seats")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_seat_map_shows_purchased(auth_client):
    """Testa que assentos comprados aparecem como 'purchased' no mapa."""
    movie = await auth_client.post("/movies/", json={
        "title": "Test Movie", "duration_minutes": 120
    })
    room = await auth_client.post("/rooms/", json={
        "name": "Sala 2", "rows": 1, "seats_per_row": 3
    })
    session = await auth_client.post("/sessions/", json={
        "movie_id": movie.json()["id"],
        "room_id": room.json()["id"],
        "starts_at": "2026-12-01T19:00:00",
    })

    # Pega o seat map para saber o ID do primeiro assento
    with patch("app.services.seat_map.aioredis.from_url") as mock_redis:
        mock_instance = AsyncMock()
        mock_instance.exists = AsyncMock(return_value=False)
        mock_instance.aclose = AsyncMock()
        mock_redis.return_value = mock_instance
        seat_map = await auth_client.get(f"/sessions/{session.json()['id']}/seats")
    seat_id = seat_map.json()["seats"][0]["seat_id"]

    # Reserva o assento (mock Redis)
    with patch("app.services.reservation.aioredis.from_url") as mock_redis:
        mock_instance = AsyncMock()
        mock_instance.set = AsyncMock(return_value=True)
        mock_instance.aclose = AsyncMock()
        mock_redis.return_value = mock_instance
        await auth_client.post("/reservations/", json={
            "session_id": session.json()["id"],
            "seat_id": seat_id,
        })

    # Checkout (mock Redis owner check)
    with patch("app.services.ticket.aioredis.from_url") as mock_redis:
        mock_instance = AsyncMock()
        mock_instance.get = AsyncMock(return_value=b"1")  # user_id = 1
        mock_instance.delete = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_redis.return_value = mock_instance
        checkout_resp = await auth_client.post("/tickets/checkout", json={
            "session_id": session.json()["id"],
            "seat_id": seat_id,
        })
        assert checkout_resp.status_code == 201

    # Agora verifica o seat map — assento deve estar 'purchased'
    with patch("app.services.seat_map.aioredis.from_url") as mock_redis:
        mock_instance = AsyncMock()
        mock_instance.exists = AsyncMock(return_value=False)
        mock_instance.aclose = AsyncMock()
        mock_redis.return_value = mock_instance
        response = await auth_client.get(f"/sessions/{session.json()['id']}/seats")

    data = response.json()
    purchased = [s for s in data["seats"] if s["status"] == "purchased"]
    assert len(purchased) == 1
    assert purchased[0]["seat_id"] == seat_id
