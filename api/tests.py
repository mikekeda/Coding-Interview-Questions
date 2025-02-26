import os
import sqlite3
import pytest
from sanic_testing import TestManager

from api.app import app as sanic_app

# Override the DB path for tests
sanic_app.config.DATABASE = "test.db"

# Initialize TestManager for your Sanic app
TestManager(sanic_app)


@pytest.fixture(scope="session", autouse=True)
def setup_db_once():
    """
    Create the test.db table once for the entire test session (synchronous).
    Then remove the file after all tests finish.
    """
    # 1) Create the DB/table
    conn = sqlite3.connect("test.db")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS problems(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        problem TEXT NOT NULL,
        company TEXT,
        source TEXT,
        difficulty TEXT,
        data_structures TEXT,
        algorithms TEXT,
        tags TEXT,
        time_complexity TEXT,
        space_complexity TEXT,
        passes_allowed INTEGER,
        edge_cases TEXT,
        input_types TEXT,
        output_types TEXT,
        hints TEXT,
        solution TEXT,
        code_solution TEXT
    )"""
    )
    # Insert a minimal row for id=1
    conn.execute(
        """
        INSERT INTO problems(id, title, problem)
        VALUES (1, 'Two Sum', 'Given an array of integers...')
        """
    )
    # Insert a second row for id=2 with company=Google, difficulty=Easy, and some data structures
    conn.execute(
        """
        INSERT INTO problems(
            id,
            title,
            problem,
            company,
            difficulty,
            data_structures
        )
        VALUES (
            2,
            'Climbing Stairs',
            'You can climb 1 or 2 steps...',
            'Google',
            'Easy',
            '["Array", "DP"]'
        )
        """
    )
    conn.commit()
    conn.close()

    # 2) yield => run all tests
    yield

    # 3) remove test.db after all tests
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest.mark.asyncio
async def test_list_problems_no_filters():
    """
    Test GET /api/problems with no filters (default limit=20)
    """
    request, response = await sanic_app.asgi_client.get("/api/problems")
    assert response.status_code == 200
    data = response.json
    assert "problems" in data
    assert "total" in data
    assert isinstance(data["problems"], list)
    assert isinstance(data["total"], int)
    assert data["total"] >= 2


@pytest.mark.asyncio
async def test_list_problems_with_filters():
    """
    Test GET /api/problems with some query params
    e.g. ?company=Google&difficulty=Medium
    (Adjust or skip if your DB doesn't have these values)
    """
    request, response = await sanic_app.asgi_client.get(
        "/api/problems?company=Google&difficulty=Easy"
    )
    assert response.status_code == 200
    data = response.json
    # We can't guarantee how many results, but we can check structure
    assert "problems" in data
    assert "total" in data
    # Optionally ensure that the results actually match "company=Google" and "difficulty=Easy"
    for p in data["problems"]:
        assert p["company"] == "Google"
        assert p["difficulty"] == "Easy"


@pytest.mark.asyncio
async def test_get_problem_found():
    """
    Test GET /api/problems/<problem_id>
    We'll assume problem with id=1 exists in the DB
    Adjust as needed
    """
    request, response = await sanic_app.asgi_client.get("/api/problems/1")
    assert response.status_code == 200
    data = response.json
    assert "id" in data
    assert data["id"] == 1


@pytest.mark.asyncio
async def test_get_problem_not_found():
    """
    Test GET /api/problems/<problem_id> for a non-existing problem
    """
    request, response = await sanic_app.asgi_client.get("/api/problems/9999999")
    assert response.status_code == 404
    assert response.json["error"] == "Problem not found"


@pytest.mark.asyncio
async def test_facets_no_filters():
    """
    Test GET /api/facets with no filters
    Should return facet counts for company, difficulty, data_structures
    """
    request, response = await sanic_app.asgi_client.get("/api/facets")
    assert response.status_code == 200
    data = response.json

    # We expect top-level keys: company, difficulty, data_structures
    assert "company" in data
    assert "difficulty" in data
    assert "data_structures" in data

    google_facet = next(
        (item for item in data["company"] if item["value"] == "Google"), None
    )
    assert google_facet is not None
    assert google_facet["count"] == 1


@pytest.mark.asyncio
async def test_facets_with_filters():
    """
    Test GET /api/facets with some filters
    e.g. company=Google => only rows that match 'Google'
    """
    request, response = await sanic_app.asgi_client.get("/api/facets?company=Google")
    assert response.status_code == 200
    data = response.json
    # same structure checks
    assert "company" in data
    assert "difficulty" in data
    assert "data_structures" in data

    easy_facet = next(
        (item for item in data["difficulty"] if item["value"] == "Easy"), None
    )
    assert easy_facet is not None
    assert easy_facet["count"] == 1


@pytest.mark.asyncio
async def test_sitemap():
    """
    Test GET /sitemap.xml
    """
    request, response = await sanic_app.asgi_client.get("/sitemap.xml")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/xml"
    content = response.text
    assert "<urlset" in content
    assert "</urlset>" in content
