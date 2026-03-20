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