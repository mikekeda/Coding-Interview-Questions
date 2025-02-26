import json as jsonlib  # to avoid confusion with sanic.response.json
import aiosqlite
from sanic import Sanic
from sanic.response import json, text
from sanic_cors import CORS

from api.settings import SANIC_CONFIG

app = Sanic("CodingInterviewQuestionsApp")
app.config.update(SANIC_CONFIG)
CORS(app, resources={r"/*": {"origins": app.config.DOMAIN}})


# Helper: decode JSON string fields into lists
def decode_fields(problem):
    json_fields = [
        "data_structures",
        "algorithms",
        "tags",
        "edge_cases",
        "input_types",
        "output_types",
        "hints",
    ]
    for field in json_fields:
        if problem.get(field):
            try:
                problem[field] = jsonlib.loads(problem[field])
            except Exception:
                problem[field] = []
        else:
            problem[field] = []
    return problem


def build_where_clause(request):
    """
    Reads query params (company, difficulty, search, data_structure)
    and returns (where_sql, parameters).
    """
    where_sql = "WHERE 1=1"
    parameters = []

    company = request.args.get("company")
    if company:
        where_sql += " AND company = ?"
        parameters.append(company)

    difficulty = request.args.get("difficulty")
    if difficulty:
        where_sql += " AND difficulty = ?"
        parameters.append(difficulty)

    search = request.args.get("search")
    if search:
        where_sql += " AND title LIKE ?"
        parameters.append(f"%{search}%")

    data_structure = request.args.get("data_structure")
    if data_structure:
        where_sql += " AND data_structures LIKE ?"
        parameters.append(f'%"{data_structure}"%')

    return where_sql, parameters


@app.get("/api/facets")
async def list_facets(request):
    # 1) Build the same WHERE clause
    where_sql, parameters = build_where_clause(request)

    # 2) We'll do separate queries for each dimension

    # 2a) Company facet
    # Example: SELECT company, COUNT(*) as cnt FROM problems WHERE ... GROUP BY company
    company_facet_sql = (
        f"SELECT company, COUNT(*) as cnt FROM problems {where_sql} GROUP BY company"
    )

    # 2b) Difficulty facet
    difficulty_facet_sql = f"SELECT difficulty, COUNT(*) as cnt FROM problems {where_sql} GROUP BY difficulty"

    # 2c) Data structures require reading each row, parsing JSON, counting in Python

    async with aiosqlite.connect(app.config.DATABASE) as db:
        db.row_factory = aiosqlite.Row

        # 3) Company facet
        company_facet_data = []
        cursor = await db.execute(company_facet_sql, parameters)
        rows = await cursor.fetchall()
        for row in rows:
            if row["company"]:
                company_facet_data.append(
                    {"value": row["company"], "count": row["cnt"]}
                )

        # 4) Difficulty facet
        difficulty_facet_data = []
        cursor = await db.execute(difficulty_facet_sql, parameters)
        rows = await cursor.fetchall()
        for row in rows:
            if row["difficulty"]:
                difficulty_facet_data.append(
                    {"value": row["difficulty"], "count": row["cnt"]}
                )

        # We want to sort the difficulties in the order: Easy, Medium, Hard
        ORDER_MAP = {"Easy": 0, "Medium": 1, "Hard": 2}
        # Sort the list in place using the custom order map
        difficulty_facet_data.sort(key=lambda item: ORDER_MAP.get(item["value"], 999))

        # 5) Data structures facet
        # We can't easily group by data_structures if it's JSON,
        # so we fetch all matching rows, parse the JSON, accumulate counts.
        ds_count = {}
        ds_query = f"SELECT data_structures FROM problems {where_sql}"
        cursor = await db.execute(ds_query, parameters)
        rows = await cursor.fetchall()
        for row in rows:
            ds_field = row["data_structures"]
            if ds_field:
                try:
                    ds_list = jsonlib.loads(ds_field)
                    for ds in ds_list:
                        ds_count[ds] = ds_count.get(ds, 0) + 1
                except:
                    pass
        data_structures_facet_data = []
        for ds, cnt in ds_count.items():
            data_structures_facet_data.append({"value": ds, "count": cnt})

        # sort by count
        data_structures_facet_data.sort(key=lambda x: x["count"], reverse=True)

    # 6) Return them all
    return json(
        {
            "company": company_facet_data,
            "difficulty": difficulty_facet_data,
            "data_structures": data_structures_facet_data,
        }
    )


@app.get("/api/problems")
async def list_problems(request):
    where_sql, parameters = build_where_clause(request)

    sort_order = request.args.get("sort_order", "asc").lower()
    if sort_order not in {"asc", "desc"}:
        sort_order = "asc"

    limit = int(request.args.get("limit", 20))
    offset = int(request.args.get("offset", 0))

    query = (
        f"SELECT * FROM problems {where_sql} ORDER BY id {sort_order} LIMIT ? OFFSET ?"
    )
    parameters_for_query = parameters + [limit, offset]

    count_query = f"SELECT COUNT(*) as total FROM problems {where_sql}"

    problems_list = []
    async with aiosqlite.connect(app.config.DATABASE) as db:
        db.row_factory = aiosqlite.Row

        # 1) Get total count
        cursor_count = await db.execute(count_query, parameters)
        row_count = await cursor_count.fetchone()
        total = row_count["total"] if row_count else 0

        # 2) Get the actual rows
        cursor = await db.execute(query, parameters_for_query)
        rows = await cursor.fetchall()
        for row in rows:
            problem = dict(row)
            problems_list.append(decode_fields(problem))  # decode_fields as needed

    return json({"problems": problems_list, "total": total})


@app.get("/api/problems/<problem_id:int>")
async def get_problem(request, problem_id):
    async with aiosqlite.connect(app.config.DATABASE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
        row = await cursor.fetchone()
        if row is None:
            return json({"error": "Problem not found"}, status=404)
        problem = dict(row)
        return json(decode_fields(problem))


@app.get("/sitemap.xml")
async def sitemap_xml(request):
    # 1) Basic static pages
    url_entries = [
        f"""
        <url>
            <loc>{app.config.DOMAIN}/</loc>
            <priority>1.0</priority>
        </url>
        <url>
            <loc>{app.config.DOMAIN}/about</loc>
            <priority>0.8</priority>
        </url>
        """
    ]

    # 2) Query all problem IDs
    async with aiosqlite.connect(app.config.DATABASE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT id FROM problems")
        rows = await cursor.fetchall()

    for row in rows:
        problem_id = row["id"]
        url_entries.append(
            f"""
    <url>
        <loc>{app.config.DOMAIN}/problems/{problem_id}</loc>
        <priority>0.8</priority>
    </url>"""
        )

    # Join them into a valid sitemap XML
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{''.join(url_entries)}
</urlset>"""

    # 3) Return as XML
    return text(sitemap_content, content_type="application/xml")


if __name__ == "__main__":
    # Run on port 8000 (adjust as needed)
    app.run(host="0.0.0.0", port=8000, debug=True)
