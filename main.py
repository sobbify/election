from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import database
import uuid
import os

app = FastAPI()

# Resolve paths relative to this file's location so they work in any environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure static and templates directories exist
os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "templates"), exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

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
async def add_question(election_id: int, text: str = Form(...), db: Session = Depends(get_db)):
    question = database.Question(text=text, election_id=election_id)
    db.add(question)
    db.commit()
    return RedirectResponse(url=f"/admin/election/{election_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/question/{question_id}/option/add")
async def add_option(question_id: int, name: str = Form(...), bio: str = Form(None), db: Session = Depends(get_db)):
    question = db.query(database.Question).filter(database.Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    option = database.Option(name=name, bio=bio, question_id=question_id)
    db.add(option)
    db.commit()
    return RedirectResponse(url=f"/admin/election/{question.election_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/election/{election_id}/voter/add")
async def add_voter(election_id: int, voter_id: str = Form(...), db: Session = Depends(get_db)):
    voter_key = str(uuid.uuid4())[:8]
    voter = database.Voter(voter_id=voter_id, voter_key=voter_key, election_id=election_id)
    db.add(voter)
    db.commit()
    return RedirectResponse(url=f"/admin/election/{election_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/election/{election_id}/toggle")
async def toggle_election(election_id: int, db: Session = Depends(get_db)):
    election = db.query(database.Election).filter(database.Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    election.is_active = not election.is_active
    db.commit()
    return RedirectResponse(url=f"/admin/election/{election_id}", status_code=status.HTTP_303_SEE_OTHER)

# --- Voter Routes ---

@app.get("/vote/{election_id}", response_class=HTMLResponse)
async def voter_login_page(election_id: int, request: Request, db: Session = Depends(get_db)):
    election = db.query(database.Election).filter(database.Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    return templates.TemplateResponse("voter/login.html", {"request": request, "election": election})

@app.post("/vote/{election_id}/login")
async def voter_login(election_id: int, voter_id: str = Form(...), voter_key: str = Form(...), db: Session = Depends(get_db)):
    voter = db.query(database.Voter).filter(
        database.Voter.election_id == election_id,
        database.Voter.voter_id == voter_id,
        database.Voter.voter_key == voter_key
    ).first()
    if not voter:
        return RedirectResponse(url=f"/vote/{election_id}?error=Invalid credentials", status_code=status.HTTP_303_SEE_OTHER)
    if voter.has_voted:
        return RedirectResponse(url=f"/vote/{election_id}/results", status_code=status.HTTP_303_SEE_OTHER)
    
    return RedirectResponse(url=f"/vote/{election_id}/ballot?voter_id={voter_id}&voter_key={voter_key}", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/vote/{election_id}/ballot", response_class=HTMLResponse)
async def voter_ballot(election_id: int, voter_id: str, voter_key: str, request: Request, db: Session = Depends(get_db)):
    election = db.query(database.Election).filter(database.Election.id == election_id).first()
    if not election or not election.is_active:
        return HTMLResponse(content="Election is not active.", status_code=403)
    
    voter = db.query(database.Voter).filter(
        database.Voter.election_id == election_id,
        database.Voter.voter_id == voter_id,
        database.Voter.voter_key == voter_key
    ).first()
    if not voter or voter.has_voted:
        return HTMLResponse(content="Unauthorized or already voted.", status_code=403)

    return templates.TemplateResponse("voter/ballot.html", {"request": request, "election": election, "voter_id": voter_id, "voter_key": voter_key})

@app.post("/vote/{election_id}/submit")
async def submit_vote(election_id: int, request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    voter_id = form_data.get("voter_id")
    voter_key = form_data.get("voter_key")
    
    voter = db.query(database.Voter).filter(
        database.Voter.election_id == election_id,
        database.Voter.voter_id == voter_id,
        database.Voter.voter_key == voter_key
    ).first()
    
    if not voter or voter.has_voted:
        return HTMLResponse(content="Unauthorized or already voted.", status_code=403)
    
    for key, value in form_data.items():
        if key.startswith("question_"):
            option_id = int(value)
            option = db.query(database.Option).filter(database.Option.id == option_id).first()
            if option:
                option.votes += 1
    
    voter.has_voted = True
    db.commit()
    return RedirectResponse(url=f"/vote/{election_id}/results", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/vote/{election_id}/results", response_class=HTMLResponse)
async def view_results(election_id: int, request: Request, db: Session = Depends(get_db)):
    election = db.query(database.Election).filter(database.Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    return templates.TemplateResponse("voter/results.html", {"request": request, "election": election})
