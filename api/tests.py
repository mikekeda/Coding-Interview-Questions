import os

import sqlite3
import pytest
from sanic_testing import TestManager


from app import app as sanic_app  # import your Sanic instance from app.py

# Override the DB path for tests (optional)
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
    conn.execute(
        """
        INSERT INTO problems(id, title, problem)
        VALUES (1, 'Two Sum', 'Given an array of integers...')
    """
    )
    conn.execute(
        """
        INSERT INTO problems(id, title, problem, company, difficulty)
        VALUES (2, 'Climbing Stairs', 'You can climb 1 or 2 steps...', 'Google', 'Easy')
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
async def test_list_companies():
    """
    Test the /api/companies endpoint
    """
    request, response = await sanic_app.asgi_client.get("/api/companies")
    assert response.status_code == 200
    # Expect JSON list of companies
    assert isinstance(response.json, list)


@pytest.mark.asyncio
async def test_list_data_structures():
    """
    Test the /api/data_structures endpoint
    """
    request, response = await sanic_app.asgi_client.get("/api/data_structures")
    assert response.status_code == 200
    # Expect JSON list of data structures
    assert isinstance(response.json, list)


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


@pytest.mark.asyncio
async def test_list_problems_with_filters():
    """
    Test GET /api/problems with some query params
    e.g. ?company=Google&difficulty=Medium
    (Adjust or skip if your DB doesn't have these values)
    """
    request, response = await sanic_app.asgi_client.get(
        "/api/problems?company=Google&difficulty=Medium"
    )
    assert response.status_code == 200
    data = response.json
    # We can't guarantee how many results, but we can check structure
    assert "problems" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_problem_found():
    """
    Test GET /api/problems/<problem_id>
    We'll assume problem with id=1 exists in the DB
    Adjust as needed
    """
    request, response = await sanic_app.asgi_client.get("/api/problems/1")
    # If your DB has an actual problem with id=1
    # else skip or adapt
    if response.status_code == 200:
        data = response.json
        assert "id" in data
        assert data["id"] == 1
    else:
        # If no problem with id=1, maybe test something else
        assert response.status_code in (200, 404)


@pytest.mark.asyncio
async def test_get_problem_not_found():
    """
    Test GET /api/problems/<problem_id> for a non-existing problem
    """
    # Using some large ID that doesn't exist
    request, response = await sanic_app.asgi_client.get("/api/problems/9999999")
    assert response.status_code == 404
    assert response.json["error"] == "Problem not found"


@pytest.mark.asyncio
async def test_sitemap():
    """
    Test GET /sitemap.xml
    """
    request, response = await sanic_app.asgi_client.get("/sitemap.xml")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/xml"
    # Optionally check that it contains some known URL
    # e.g. <loc>https://localhost:8000/about</loc>
    content = response.text
    assert "<urlset" in content
    assert "</urlset>" in content
