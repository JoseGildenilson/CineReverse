import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_reserve_seat(auth_client):
    movie = await auth_client.post("/movies/", json={
        "title": "Test Movie", "duration_minutes": 120
    })
    room = await auth_client.post("/rooms/", json={
        "name": "Sala 1", "rows": 2, "seats_per_row": 5
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

    with patch("app.services.reservation.aioredis.from_url") as mock_redis:
        mock_instance = AsyncMock()
        mock_instance.set = AsyncMock(return_value=True)
        mock_instance.aclose = AsyncMock()
        mock_redis.return_value = mock_instance

        response = await auth_client.post("/reservations/", json={
            "session_id": session.json()["id"],
            "seat_id": seat_id,
        })
        assert response.status_code == 201
        assert response.json()["seat_id"] == seat_id


@pytest.mark.asyncio
async def test_reserve_already_purchased_seat(auth_client):
    movie = await auth_client.post("/movies/", json={
        "title": "Test Movie", "duration_minutes": 120
    })
    room = await auth_client.post("/rooms/", json={
        "name": "Sala 1", "rows": 2, "seats_per_row": 5
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

    with patch("app.services.reservation.aioredis.from_url") as mock_redis:
        mock_instance = AsyncMock()
        mock_instance.set = AsyncMock(return_value=False)
        mock_instance.aclose = AsyncMock()
        mock_redis.return_value = mock_instance

        response = await auth_client.post("/reservations/", json={
            "session_id": session.json()["id"],
            "seat_id": seat_id,
        })
        assert response.status_code == 409


@pytest.mark.asyncio
async def test_release_seat_success(auth_client):
    movie = await auth_client.post("/movies/", json={
        "title": "Test Movie", "duration_minutes": 120
    })
    room = await auth_client.post("/rooms/", json={
        "name": "Sala 1", "rows": 2, "seats_per_row": 5
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

    # Reserva
    with patch("app.services.reservation.aioredis.from_url") as mock_redis:
        mock_instance = AsyncMock()
        mock_instance.set = AsyncMock(return_value=True)
        mock_instance.aclose = AsyncMock()
        mock_redis.return_value = mock_instance
        await auth_client.post("/reservations/", json={
            "session_id": session.json()["id"],
            "seat_id": seat_id,
        })

    # Libera
    with patch("app.services.reservation.aioredis.from_url") as mock_redis:
        mock_instance = AsyncMock()
        mock_instance.get = AsyncMock(return_value=b"1")
        mock_instance.delete = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_redis.return_value = mock_instance
        response = await auth_client.delete(
            f"/reservations/{session.json()['id']}/{seat_id}"
        )
    assert response.status_code == 200
    assert response.json()["message"] == "Reservation released successfully"


@pytest.mark.asyncio
async def test_release_seat_not_owner(auth_client):
    with patch("app.services.reservation.aioredis.from_url") as mock_redis:
        mock_instance = AsyncMock()
        mock_instance.get = AsyncMock(return_value=b"999")  # outro user
        mock_instance.aclose = AsyncMock()
        mock_redis.return_value = mock_instance
        response = await auth_client.delete("/reservations/1/1")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_reserve_session_not_found(auth_client):
    response = await auth_client.post("/reservations/", json={
        "session_id": 9999,
        "seat_id": 1,
    })
    assert response.status_code == 404