from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import database
import utils
import uuid
import os
from pathlib import Path

app = FastAPI()

# Get the directory where main.py is located
BASE_DIR = Path(__file__).parent

# Ensure directories exist
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
UPLOADS_DIR = STATIC_DIR / "uploads"

STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Initialize DB
database.init_db()

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Admin Routes ---

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    elections = db.query(database.Election).all()
    return templates.TemplateResponse("admin/dashboard.html", {"request": request, "elections": elections})

@app.post("/admin/election/create")
async def create_election(title: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    new_election = database.Election(title=title, description=description)
    db.add(new_election)
    db.commit()
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/admin/election/{election_id}", response_class=HTMLResponse)
async def election_detail(election_id: int, request: Request, db: Session = Depends(get_db)):
    election = db.query(database.Election).filter(database.Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    return templates.TemplateResponse("admin/election_detail.html", {"request": request, "election": election})

@app.post("/admin/election/{election_id}/question/add")
async def add_question(
    election_id: int,
    text: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    image_path = None
    if image and image.filename:
        file_data = await image.read()
        filename = f"q_{election_id}_{uuid.uuid4().hex[:8]}.jpg"
        image_path = utils.save_image(file_data, filename)
    
    question = database.Question(
        text=text,
        election_id=election_id,
        image_path=image_path
    )
    db.add(question)
    db.commit()
    return RedirectResponse(url=f"/admin/election/{election_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/question/{question_id}/option/add")
async def add_option(
    question_id: int,
    name: str = Form(...),
    bio: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    question = db.query(database.Question).filter(database.Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    image_path = None
    if image and image.filename:
        file_data = await image.read()
        filename = f"o_{question_id}_{uuid.uuid4().hex[:8]}.jpg"
        image_path = utils.save_image(file_data, filename)
    
    option = database.Option(
        name=name,
        bio=bio,
        question_id=question_id,
        image_path=image_path
    )
    db.add(option)
    db.commit()
    return RedirectResponse(url=f"/admin/election/{question.election_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/election/{election_id}/toggle")
async def toggle_election(election_id: int, db: Session = Depends(get_db)):
    election = db.query(database.Election).filter(database.Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    election.is_active = not election.is_active
    db.commit()
    return RedirectResponse(url=f"/admin/election/{election_id}", status_code=status.HTTP_303_SEE_OTHER)

# --- Vote Management ---

@app.post("/admin/election/{election_id}/votes/clear")
async def clear_all_votes(election_id: int, db: Session = Depends(get_db)):
    election = db.query(database.Election).filter(database.Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    
    # Reset all votes for this election
    for question in election.questions:
        for option in question.options:
            option.votes = 0
    
    db.commit()
    return RedirectResponse(url=f"/admin/election/{election_id}", status_code=status.HTTP_303_SEE_OTHER)

# --- Voter Routes (Open Voting) ---

@app.get("/vote/{election_id}", response_class=HTMLResponse)
async def voter_ballot_page(election_id: int, request: Request, db: Session = Depends(get_db)):
    election = db.query(database.Election).filter(database.Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    if not election.is_active:
        return HTMLResponse(content="<div class='text-center p-8'><h1 class='text-2xl font-bold'>Election is not active</h1></div>", status_code=403)
    return templates.TemplateResponse("voter/ballot.html", {"request": request, "election": election})

@app.post("/vote/{election_id}/submit")
async def submit_vote(election_id: int, request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    
    election = db.query(database.Election).filter(database.Election.id == election_id).first()
    if not election or not election.is_active:
        return HTMLResponse(content="Election is not active.", status_code=403)
    
    # Process votes directly without thread pool overhead
    for key, value in form_data.items():
        if key.startswith("question_"):
            try:
                option_id = int(value)
                option = db.query(database.Option).filter(database.Option.id == option_id).first()
                if option:
                    option.votes += 1
            except (ValueError, TypeError):
                pass
    
    db.commit()
    return RedirectResponse(url=f"/vote/{election_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/vote/{election_id}/results", response_class=HTMLResponse)
async def view_results(election_id: int, request: Request, db: Session = Depends(get_db)):
    election = db.query(database.Election).filter(database.Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    return templates.TemplateResponse("voter/results.html", {"request": request, "election": election})
