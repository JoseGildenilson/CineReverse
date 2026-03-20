import pytest


@pytest.mark.asyncio
async def test_create_movie(auth_client):
    response = await auth_client.post("/movies/", json={
        "title": "Inception",
        "description": "A mind-bending thriller",
        "duration_minutes": 148,
    })
    assert response.status_code == 201
    assert response.json()["title"] == "Inception"


@pytest.mark.asyncio
async def test_create_movie_unauthenticated(client):
    response = await client.post("/movies/", json={
        "title": "Inception",
        "duration_minutes": 148,
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_movies(auth_client):
    await auth_client.post("/movies/", json={"title": "Movie 1", "duration_minutes": 90})
    await auth_client.post("/movies/", json={"title": "Movie 2", "duration_minutes": 120})
    response = await auth_client.get("/movies/")
    assert response.status_code == 200
    assert response.json()["total"] == 2


@pytest.mark.asyncio
async def test_get_movie_not_found(client):
    response = await client.get("/movies/999")
    assert response.status_code == 404