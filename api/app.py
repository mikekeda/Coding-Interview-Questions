import json as jsonlib  # to avoid confusion with sanic.response.json
import aiosqlite
from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS

from api.settings import SANIC_CONFIG

app = Sanic("CodingInterviewQuestionsApp")
app.config.update(SANIC_CONFIG)
CORS(app)  # enable CORS so our React app can call the API

DATABASE = "problems.db"


# Helper: decode JSON string fields into lists
def decode_fields(problem):
    json_fields = [
        'data_structures', 'algorithms', 'tags',
        'edge_cases', 'input_types', 'output_types', 'hints'
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


@app.get('/api/companies')
async def list_companies(request):
    companies = []
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            'SELECT DISTINCT company FROM problems WHERE company IS NOT NULL AND company != ""'
        )
        rows = await cursor.fetchall()
        for row in rows:
            companies.append(row['company'])
    return json(companies)


@app.get('/api/data_structures')
async def list_data_structures(request):
    ds_set = set()
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('SELECT data_structures FROM problems')
        rows = await cursor.fetchall()
        for row in rows:
            if row['data_structures']:
                try:
                    ds_list = jsonlib.loads(row['data_structures'])
                    for ds in ds_list:
                        ds_set.add(ds)
                except:
                    pass
    # Return a sorted list
    data_structures = sorted(ds_set)
    return json(data_structures)


@app.get('/api/problems')
async def list_problems(request):
    query = "SELECT * FROM problems WHERE 1=1"
    count_query = "SELECT COUNT(*) as total FROM problems WHERE 1=1"
    parameters = []
    count_parameters = []

    # Filtering by company
    company = request.args.get('company')
    if company:
        query += " AND company = ?"
        count_query += " AND company = ?"
        parameters.append(company)
        count_parameters.append(company)

    # Filtering by difficulty
    difficulty = request.args.get('difficulty')
    if difficulty:
        query += " AND difficulty = ?"
        count_query += " AND difficulty = ?"
        parameters.append(difficulty)
        count_parameters.append(difficulty)

    # Searching by title (for example)
    search = request.args.get('search')
    if search:
        # Use LIKE to match any substring
        query += " AND title LIKE ?"
        count_query += " AND title LIKE ?"
        like_value = f"%{search}%"
        parameters.append(like_value)
        count_parameters.append(like_value)

    # Filtering by data_structure
    data_structure = request.args.get('data_structure')
    if data_structure:
        query += " AND data_structures LIKE ?"
        count_query += " AND data_structures LIKE ?"
        like_value = f'%"{data_structure}"%'
        parameters.append(like_value)
        count_parameters.append(like_value)

    # Pagination
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    query += " LIMIT ? OFFSET ?"
    parameters.extend([limit, offset])

    problems_list = []
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row

        # 1) Get total count
        cursor_count = await db.execute(count_query, count_parameters)
        row_count = await cursor_count.fetchone()
        total = row_count['total'] if row_count else 0

        # 2) Get the actual rows
        cursor = await db.execute(query, parameters)
        rows = await cursor.fetchall()
        for row in rows:
            problem = dict(row)
            problems_list.append(decode_fields(problem))  # decode_fields as needed

    return json({
        "problems": problems_list,
        "total": total
    })


@app.get('/api/problems/<problem_id:int>')
async def get_problem(request, problem_id):
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('SELECT * FROM problems WHERE id = ?', (problem_id,))
        row = await cursor.fetchone()
        if row is None:
            return json({'error': 'Problem not found'}, status=404)
        problem = dict(row)
        return json(decode_fields(problem))


if __name__ == '__main__':
    # Run on port 8000 (adjust as needed)
    app.run(host="0.0.0.0", port=8000, debug=True)
