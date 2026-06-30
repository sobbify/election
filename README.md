# Election Runner Clone (FastAPI)

A secure, real-time online election application built with FastAPI, SQLAlchemy (SQLite), and Chart.js.

## Features
- **Admin Dashboard**: Create elections, add questions, and manage candidates.
- **Voter Management**: Generate unique voter keys and track voting status.
- **Secure Voting**: One-time voting per voter key.
- **Real-time Results**: Visualized results using Chart.js.

## Installation

1. Install the locked dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

3. Open your browser to `http://127.0.0.1:8000`.

## Admin Usage
- Go to `/admin` to create your first election.
- Add positions (questions) and candidates (options) to the ballot.
- Add eligible voters to generate their unique keys.
- **Launch** the election to allow voting.
- Share the `/vote/{id}` link with your voters.

## Technologies Used
- **Backend**: FastAPI
- **Database**: SQLAlchemy with SQLite
- **Frontend**: Jinja2 Templates, Tailwind CSS, Chart.js
- **Environment**: Python 3.11+
