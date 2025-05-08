from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from solver import solve_equation_with_steps

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str

@app.post("/api/solve")
def api_solve(q: Question):
    try:
        result = solve_equation_with_steps(q.question)
        return {
            "solution": result["solution"],
            "steps": result["steps"].split("\n")  # Split steps into a list for frontend
        }
    except Exception as e:
        return {"detail": str(e)}