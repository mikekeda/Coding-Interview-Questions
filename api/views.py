from sanic.exceptions import InvalidUsage
from sanic.response import json, text
from sqlalchemy import func, select

from api.app import app
from api.models import Problem, DifficultyEnum


def build_filters(request):
    """
    Read query params (company, difficulty, data_structure, search, algorithm, tags)
    and return a list of SQLAlchemy filter expressions.
    """
    filters = []

    # Filter by Company
    company = request.args.get("company")
    if company:
        filters.append(Problem.company == company)

    # Filter by Difficulty
    difficulty = request.args.get("difficulty")
    if difficulty:
        try:
            filters.append(Problem.difficulty == DifficultyEnum(difficulty).value)
        except ValueError:
            raise InvalidUsage("Invalid difficulty value for filter")

    # Filter by Title Search
    search = request.args.get("search")
    if search:
        filters.append(Problem.title.ilike(f"%{search}%"))

    # Filter by Data Structure
    data_structure = request.args.get("data_structure")
    if data_structure:
        # For a JSONB column containing an array of data structures
        filters.append(Problem.data_structures.contains([data_structure]))

    # Filter by Algorithm
    algorithm = request.args.get("algorithm")
    if algorithm:
        # For a JSONB column containing an array of algorithms
        filters.append(Problem.algorithms.contains([algorithm]))

    # Filter by Tags (multiple)
    tag = request.args.get("tag")  # returns a list of all 'tags' params
    if tag:
        filters.append(Problem.tags.contains([tag]))

    return filters


@app.get("/api/facets")
async def list_facets(request):
    session = request.ctx.session
    filters = build_filters(request)

    # --- 1. Company Facets ---
    company_stmt = (
        select(Problem.company, func.count(Problem.id).label("cnt"))
        .where(*filters)
        .group_by(Problem.company)
    )
    result = await session.execute(company_stmt)
    company_facets = [
        {"value": row.company, "count": row.cnt}
        for row in result.fetchall()
        if row.company
    ]

    # --- 2. Difficulty Facets ---
    difficulty_stmt = (
        select(Problem.difficulty, func.count(Problem.id).label("cnt"))
        .where(*filters)
        .group_by(Problem.difficulty)
    )
    result = await session.execute(difficulty_stmt)
    difficulty_facets = [
        {"value": row.difficulty, "count": row.cnt}
        for row in result.fetchall()
        if row.difficulty
    ]

    # Sort difficulties in order: Easy, Medium, Hard
    ORDER_MAP = {"Easy": 0, "Medium": 1, "Hard": 2}
    difficulty_facets.sort(key=lambda item: ORDER_MAP.get(item["value"], 999))

    # --- 3. Data Structures Facets (JSONB array) ---
    ds_stmt = select(Problem.data_structures).where(*filters)
    result = await session.execute(ds_stmt)
    ds_count = {}
    for row in result.fetchall():
        ds_list = row[0]  # data_structures column
        if ds_list and isinstance(ds_list, list):
            for ds in ds_list:
                ds_count[ds] = ds_count.get(ds, 0) + 1

    data_structures_facets = [
        {"value": ds, "count": count} for ds, count in ds_count.items()
    ]
    data_structures_facets.sort(key=lambda x: x["count"], reverse=True)

    # --- 4. Algorithms Facets (JSONB array) ---
    alg_stmt = select(Problem.algorithms).where(*filters)
    result = await session.execute(alg_stmt)
    alg_count = {}
    for row in result.fetchall():
        alg_list = row[0]  # algorithms column
        if alg_list and isinstance(alg_list, list):
            for alg in alg_list:
                alg_count[alg] = alg_count.get(alg, 0) + 1

    algorithms_facets = [
        {"value": alg, "count": count} for alg, count in alg_count.items()
    ]
    algorithms_facets.sort(key=lambda x: x["count"], reverse=True)

    # --- 5. Tags Facets (JSONB array) ---
    tags_stmt = select(Problem.tags).where(*filters)
    result = await session.execute(tags_stmt)
    tags_count = {}
    for row in result.fetchall():
        tags_list = row[0]  # tags column
        if tags_list and isinstance(tags_list, list):
            for tag in tags_list:
                tags_count[tag] = tags_count.get(tag, 0) + 1

    tags_facets = [{"value": tag, "count": count} for tag, count in tags_count.items()]
    tags_facets.sort(key=lambda x: x["count"], reverse=True)

    # --- Return All Facets ---
    return json(
        {
            "company": company_facets,
            "difficulty": difficulty_facets,
            "data_structures": data_structures_facets,
            "algorithms": algorithms_facets,
            "tags": tags_facets,
        }
    )


@app.get("/api/problems")
async def list_problems(request):
    session = request.ctx.session
    filters = build_filters(request)

    sort_order = request.args.get("sort_order", "asc").lower()
    if sort_order not in {"asc", "desc"}:
        sort_order = "asc"

    limit = int(request.args.get("limit", 20))
    offset = int(request.args.get("offset", 0))

    # Build the query with ordering and pagination
    query = (
        select(Problem)
        .where(*filters)
        .order_by(Problem.id.asc() if sort_order == "asc" else Problem.id.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(query)
    problems = result.scalars().all()

    # Count total number of records matching the filters
    count_query = select(func.count(Problem.id)).where(*filters)
    count_result = await session.execute(count_query)
    total = count_result.scalar() or 0

    problems_list = [problem.to_dict() for problem in problems]
    return json({"problems": problems_list, "total": total})


@app.get("/api/problems/<problem_id:int>")
async def get_problem(request, problem_id):
    session = request.ctx.session
    query = select(Problem).where(Problem.id == problem_id)
    result = await session.execute(query)
    problem = result.scalar_one_or_none()
    if not problem:
        return json({"error": "Problem not found"}, status=404)
    return json(problem.to_dict())


@app.get("/sitemap.xml")
async def sitemap_xml(request):
    session = request.ctx.session
    query = select(Problem.id)
    result = await session.execute(query)
    ids = [row[0] for row in result.fetchall()]

    # Basic static pages
    url_entries = [
        f"""
        <url>
            <loc>{request.app.config.DOMAIN}/</loc>
            <priority>1.0</priority>
        </url>
        <url>
            <loc>{request.app.config.DOMAIN}/about</loc>
            <priority>0.8</priority>
        </url>
        """
    ]
    for problem_id in ids:
        url_entries.append(
            f"""
        <url>
            <loc>{request.app.config.DOMAIN}/problems/{problem_id}</loc>
            <priority>0.8</priority>
        </url>
        """
        )
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{''.join(url_entries)}
</urlset>"""
    return text(sitemap_content, content_type="application/xml")


if __name__ == "__main__":
    # Run on port 8000 (adjust as needed)
    app.run(host="0.0.0.0", port=8000, debug=True)
