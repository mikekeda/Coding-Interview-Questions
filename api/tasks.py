import logging
import re
from typing import List, Optional

import imaplib
import email
from email.header import decode_header

from openai import OpenAI
from pydantic import BaseModel
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker

from api.celery_app import app
from api.models import Problem, DifficultyEnum
from api.settings import EMAIL, EMAIL_PASSWORD, OPENAI_API_KEY, SANIC_CONFIG

engine = create_engine(
    f"postgresql://{ SANIC_CONFIG['DB_USER'] }:{ SANIC_CONFIG['DB_PASSWORD'] }"
    f"@{ SANIC_CONFIG['DB_HOST'] }/{ SANIC_CONFIG['DB_DATABASE'] }"
)
Session = sessionmaker(bind=engine)

SYSTEM_PROMPT = """
You are an AI assistant that classifies coding problems into structured data.

Given a coding problem statement, extract and return structured information in JSON format based on the following schema:

{
    "title": "Problem title extracted from the description",
    "company": "The company that asked the problem (if provided)",
    "source": "Where the problem was found (if available)",
    "difficulty": "Estimated difficulty level (Easy, Medium, or Hard)",
    "data_structures": ["List of relevant data structures used in solving the problem"],
    "algorithms": ["List of key algorithms or techniques required (e.g., Sliding Window, Two Pointers)"],
    "tags": ["List of problem categories, such as 'In-Place', 'Edge Cases', etc."],
    "time_complexity": "Expected time complexity (e.g., O(n), O(log n), etc.)",
    "space_complexity": "Expected space complexity (e.g., O(1), O(n), etc.)",
    "passes_allowed": "Number of passes over the data allowed (if mentioned)",
    "edge_cases": ["List of edge cases the problem requires handling"],
    "input_types": ["List of input types such as 'Singly Linked List', 'Integer', etc."],
    "output_types": ["List of expected output types such as 'Modified Linked List'"],
    "hints": ["List of useful hints for solving the problem"],
    "solution": "A brief high-level explanation of how to solve the problem",
    "code_solution": "A well-formatted Python solution for the problem, written in a clear and optimal way",
    "test_cases": [
        {
            "input": "Example input for a test case",
            "output": "Expected output for the test case"
        }
    ]
}

### Instructions:
- Extract the **title** based on the main task in the problem.
- Identify the **company** (if mentioned) and the **source** (if applicable).
- Estimate the **difficulty** based on constraints and known problem complexity.
- Determine relevant **data structures** and **algorithms** (e.g., Sliding Window, Two Pointers) required to solve the problem.
- Identify **tags** that classify the problem, such as "In-Place" or "Edge Cases".
- Extract **time and space complexity** based on constraints.
- If the problem restricts multiple passes, specify `passes_allowed`.
- List **common edge cases** that should be considered.
- Define **input and output types** clearly.
- Provide **hints** to guide a user in solving the problem.
- Give a concise **solution explanation**.
- The **code solution must be efficient**, using the best possible algorithm given the constraints.
- Extract **test cases** by mapping sample input to the expected output. Ensure that the extracted test cases include edge cases (for example, empty lists, lists with one element, etc.).

Respond ONLY with a valid JSON object following this schema.
"""


class TestCaseSchema(BaseModel):
    input: str
    output: str


class ProblemSchema(BaseModel):
    title: str
    company: Optional[str]  # Company that asked the question (e.g., "Google")
    source: Optional[str] = None  # e.g., "Google", "Leetcode"
    difficulty: DifficultyEnum  # e.g., "Easy", "Medium", "Hard"

    # Core attributes
    data_structures: List[str]  # e.g., ["Linked List"]
    algorithms: List[str]  # e.g., ["Two Pointers", "Sliding Window"]
    tags: List[str]  # e.g., ["In-Place", "Edge Cases"]

    # Constraints
    time_complexity: Optional[str] = None  # e.g., "O(n)"
    space_complexity: Optional[str] = None  # e.g., "O(1)"
    passes_allowed: Optional[int] = None  # e.g., 1 if single pass required

    # Additional properties
    edge_cases: List[str]  # e.g., ["Removing first node", "Removing last node"]
    input_types: List[str]  # e.g., ["Singly Linked List", "Integer"]
    output_types: List[str]  # e.g., ["Modified Linked List"]
    test_cases: List[TestCaseSchema]  # Each dict should have "input" and "output" keys

    hints: List[str]  # e.g., ["Use two pointers", "Think about edge cases"]
    solution: str  # Stores a brief solution description
    code_solution: str  # Stores a code snippet to solve the problem

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Remove Nth Node From End of List",
                "company": "Google",
                "source": "Leetcode",
                "difficulty": "Medium",
                "data_structures": ["Linked List"],
                "algorithms": ["Two Pointers", "Sliding Window"],
                "tags": ["In-Place", "Edge Cases"],
                "time_complexity": "O(n)",
                "space_complexity": "O(1)",
                "passes_allowed": 1,
                "edge_cases": ["Removing first node", "Empty list"],
                "input_types": ["Singly Linked List", "Integer"],
                "output_types": ["Modified Linked List"],
                "hints": [
                    "Use a dummy node to handle edge cases",
                    "Think about two pointers",
                ],
                "solution": "Use two pointers to locate the nth node from the end.",
                "code_solution": "def removeNthFromEnd(head, n): ...",
                "test_cases": [
                    {"input": "[1, 2, 3, 4, 5], 2", "output": "[1, 2, 3, 5]"}
                ],
            }
        }


def classify_problem(client: OpenAI, problem: str) -> ProblemSchema:
    # OPENAI_API_KEY should be set in your environment variables
    # list of models: https://platform.openai.com/docs/models
    # usage is here: https://platform.openai.com/settings/organization/usage
    # price: https://openai.com/api/pricing/
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": problem},
        ],
        response_format=ProblemSchema,
    )

    response = completion.choices[0].message.parsed

    return response


def extract_problem_body(body: str) -> str:
    candidates = [
        "This problem was recently asked by ",
        "This problem was asked by ",
        "This problem was asked ",
        "This question was asked by ",
        "Good morning! Here's your coding interview problem for today.",
    ]
    for candidate in candidates:
        try:
            start = body.index(candidate)
            break
        except ValueError:
            continue
    else:
        raise ValueError("Start string not found in email body.")

    delimiter = "--------------------------------------------------------------------------------"
    try:
        stop = body.index(delimiter, start)
    except ValueError:
        raise ValueError("Delimiter not found in email body.")

    return body[start:stop].strip()


def get_problems():
    imap = imaplib.IMAP4_SSL("imap.mail.yahoo.com")
    try:
        imap.login(EMAIL, EMAIL_PASSWORD)
    except imaplib.IMAP4.error as e:
        raise Exception("IMAP login failed") from e

    imap.select("INBOX")
    _, msgnums = imap.search(None, 'SUBJECT "Daily Coding Problem: Problem #"')
    msgnums = msgnums[0].decode("utf-8").split()
    msgnums.reverse()  # process older messages first

    for num in msgnums:
        res, msg_data = imap.fetch(str(num), "(RFC822)")
        for response in msg_data:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8")
                subject = subject.strip()

                if "Daily Coding Problem" not in subject:
                    raise Exception("Unexpected email subject format.")

                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        try:
                            extracted_body = extract_problem_body(body)
                        except ValueError as e:
                            logging.warning("Error extracting problem: %s", e)
                            continue
                        yield subject, extracted_body
                        break
    imap.close()
    imap.logout()


@app.task()
def get_new_problems():
    client = OpenAI(api_key=OPENAI_API_KEY)
    problems_added = 0

    with Session() as session:
        for subject, problem_text in get_problems():
            match = re.search(r"Problem #(\d+)", subject)
            if not match:
                logging.warning(f"Could not extract problem ID from subject: {subject}")
                continue
            problem_id = int(match.group(1))

            existing_problem = session.query(
                exists().where(Problem.id == problem_id)
            ).scalar()
            if existing_problem:
                continue

            result = classify_problem(client, problem_text)
            result = dict(result)
            result["id"] = problem_id
            # Skip first line of the problem statement
            cleaned_problem_text = problem_text.split("\n", 1)[1].strip()
            result["problem"] = cleaned_problem_text
            result["test_cases"] = [dict(v) for v in result["test_cases"]]

            session.add(Problem(**result))
            session.commit()

            logging.info(
                f"Inserted problem {problem_id}. {result['title']} into the database."
            )
            problems_added += 1

    logging.info(f"Added {problems_added} new problems.")
