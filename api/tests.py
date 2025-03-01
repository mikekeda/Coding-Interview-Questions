import os
import pytest
from sanic_testing import TestManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Override the DB settings for tests.
if os.environ.get("CODING_DB_NAME") is None:
    os.environ["CODING_DB_NAME"] = "test_coding"

from api.views import app as sanic_app
from api.models import Base, Problem

# Initialize TestManager for your Sanic app
TestManager(sanic_app)


@pytest.fixture(scope="session", autouse=True)
def setup_db_once():
    """
    Create all tables in the test database once for the entire test session,
    insert test data, then drop the tables after all tests finish.
    """
    # Create a synchronous engine using the test database configuration
    engine = create_engine(
        f"postgresql://{sanic_app.config['DB_USER']}:"
        f"{sanic_app.config['DB_PASSWORD']}@"
        f"{sanic_app.config['DB_HOST']}/"
        f"{sanic_app.config['DB_DATABASE']}"
    )

    # Drop and recreate tables to ensure a clean slate
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Insert test data
    problem1 = Problem(
        id=1,
        title="Two Sum",
        problem="Given an array of integers...",
        difficulty="Easy",
        data_structures=["Array"],
        algorithms=[],
        tags=[],
        edge_cases=[],
        input_types=[],
        output_types=[],
        test_cases=[],
        hints=[],
        solution="def two_sum(nums, target):...",
        code_solution="def two_sum(nums, target):...",
    )
    problem2 = Problem(
        id=1751,
        title="Climbing Stairs",
        problem="You can climb 1 or 2 steps...",
        company="Google",
        difficulty="Easy",
        data_structures=["Array", "DP"],
        algorithms=["Hash Table"],
        tags=[],
        edge_cases=[],
        input_types=[],
        output_types=[],
        test_cases=[],
        hints=[],
        solution="def two_sum(nums, target):...",
        code_solution="def two_sum(nums, target):...",
    )
    session.add_all([problem1, problem2])
    session.commit()
    session.close()

    yield

    # Drop all tables after tests complete
    Base.metadata.drop_all(engine)


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
    # We expect at least the two inserted problems
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_list_problems_with_filters():
    """
    Test GET /api/problems with query params.
    For example: ?company=Google&difficulty=Easy
    """
    request, response = await sanic_app.asgi_client.get(
        "/api/problems?company=Google&difficulty=Easy"
    )
    assert response.status_code == 200
    data = response.json
    assert "problems" in data
    assert "total" in data
    for p in data["problems"]:
        assert p["company"] == "Google"
        assert p["difficulty"] == "Easy"


@pytest.mark.asyncio
async def test_get_problem_found():
    """
    Test GET /api/problems/<problem_id> where the problem exists.
    """
    request, response = await sanic_app.asgi_client.get("/api/problems/1")
    assert response.status_code == 200
    data = response.json
    assert "id" in data
    assert data["id"] == 1


@pytest.mark.asyncio
async def test_get_problem_not_found():
    """
    Test GET /api/problems/<problem_id> for a non-existent problem.
    """
    request, response = await sanic_app.asgi_client.get("/api/problems/9999999")
    assert response.status_code == 404
    assert response.json["error"] == "Problem not found"


@pytest.mark.asyncio
async def test_facets_no_filters():
    """
    Test GET /api/facets with no filters.
    Should return facet counts for company, difficulty, and data_structures.
    """
    request, response = await sanic_app.asgi_client.get("/api/facets")
    assert response.status_code == 200
    data = response.json

    # Check that expected facet keys exist
    assert "company" in data
    assert "difficulty" in data
    assert "data_structures" in data

    # Verify that the facet for Google exists and has a count of 1 (from problem2)
    google_facet = next(
        (item for item in data["company"] if item["value"] == "Google"), None
    )
    assert google_facet is not None
    assert google_facet["count"] == 1


@pytest.mark.asyncio
async def test_facets_with_filters():
    """
    Test GET /api/facets with filters.
    For example, filtering by company=Google should return only rows matching Google.
    """
    request, response = await sanic_app.asgi_client.get("/api/facets?company=Google")
    assert response.status_code == 200
    data = response.json
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
    Test GET /sitemap.xml returns valid XML.
    """
    request, response = await sanic_app.asgi_client.get("/sitemap.xml")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/xml"
    content = response.text
    assert "<urlset" in content
    assert "</urlset>" in content
