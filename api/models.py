from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class Problem(Base):
    __tablename__ = 'problems'

    id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(String, nullable=False)
    problem = Column(Text, nullable=False)
    company = Column(String, nullable=True)
    source = Column(String, nullable=True)
    difficulty = Column(String, nullable=False)
    data_structures = Column(JSONB, nullable=False)
    algorithms = Column(JSONB, nullable=False)
    tags = Column(JSONB, nullable=False)
    time_complexity = Column(String, nullable=True)
    space_complexity = Column(String, nullable=True)
    passes_allowed = Column(Integer, nullable=True)
    edge_cases = Column(JSONB, nullable=False)
    input_types = Column(JSONB, nullable=False)
    output_types = Column(JSONB, nullable=False)
    test_cases = Column(JSONB, nullable=True)
    hints = Column(JSONB, nullable=False)
    solution = Column(Text, nullable=True)
    code_solution = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Problem(id={self.id}, title='{self.title}')>"

    def to_dict(self):
        """Serialize the Problem object to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "problem": self.problem,
            "company": self.company,
            "source": self.source,
            "difficulty": self.difficulty,
            "data_structures": self.data_structures,
            "algorithms": self.algorithms,
            "tags": self.tags,
            "time_complexity": self.time_complexity,
            "space_complexity": self.space_complexity,
            "passes_allowed": self.passes_allowed,
            "edge_cases": self.edge_cases,
            "input_types": self.input_types,
            "test_cases": self.test_cases,
            "output_types": self.output_types,
            "hints": self.hints,
            "solution": self.solution,
            "code_solution": self.code_solution,
        }
