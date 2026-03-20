import pytest


@pytest.mark.asyncio
async def test_create_session(auth_client):
    movie = await auth_client.post("/movies/", json={
        "title": "Test Movie", "duration_minutes": 120
    })
    room = await auth_client.post("/rooms/", json={
        "name": "Sala 1", "rows": 2, "seats_per_row": 5
    })
    response = await auth_client.post("/sessions/", json={
        "movie_id": movie.json()["id"],
        "room_id": room.json()["id"],
        "starts_at": "2026-12-01T19:00:00",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["movie_id"] == movie.json()["id"]
    assert data["room_id"] == room.json()["id"]


@pytest.mark.asyncio
async def test_create_session_unauthenticated(client):
    response = await client.post("/sessions/", json={
        "movie_id": 1,
        "room_id": 1,
        "starts_at": "2026-12-01T19:00:00",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_session_movie_not_found(auth_client):
    room = await auth_client.post("/rooms/", json={
        "name": "Sala 1", "rows": 2, "seats_per_row": 5
    })
    response = await auth_client.post("/sessions/", json={
        "movie_id": 9999,
        "room_id": room.json()["id"],
        "starts_at": "2026-12-01T19:00:00",
    })
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_sessions_by_movie(auth_client):
    movie = await auth_client.post("/movies/", json={
        "title": "Movie A", "duration_minutes": 90
    })
    room = await auth_client.post("/rooms/", json={
        "name": "Sala 1", "rows": 2, "seats_per_row": 5
    })
    await auth_client.post("/sessions/", json={
        "movie_id": movie.json()["id"],
        "room_id": room.json()["id"],
        "starts_at": "2026-12-01T15:00:00",
    })
    await auth_client.post("/sessions/", json={
        "movie_id": movie.json()["id"],
        "room_id": room.json()["id"],
        "starts_at": "2026-12-01T19:00:00",
    })
    response = await auth_client.get(f"/sessions/movie/{movie.json()['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_sessions_by_movie_not_found(auth_client):
    response = await auth_client.get("/sessions/movie/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_session(auth_client):
    movie = await auth_client.post("/movies/", json={
        "title": "Test", "duration_minutes": 100
    })
    room = await auth_client.post("/rooms/", json={
        "name": "Sala 1", "rows": 1, "seats_per_row": 5
    })
    session = await auth_client.post("/sessions/", json={
        "movie_id": movie.json()["id"],
        "room_id": room.json()["id"],
        "starts_at": "2026-12-01T20:00:00",
    })
    response = await auth_client.get(f"/sessions/{session.json()['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == session.json()["id"]


@pytest.mark.asyncio
async def test_get_session_not_found(client):
    response = await client.get("/sessions/9999")
    assert response.status_code == 404
