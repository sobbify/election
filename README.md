# VoteHub - Open Voting Platform

A modern, fast, and simple online voting application built with FastAPI, SQLAlchemy, and Chart.js. No authentication, no complexity—just open voting.

## Features

**Simple & Fast**: Create elections in seconds with an intuitive admin interface.

**Image Support**: Add images to questions and candidates for visual elections.

**Open Voting**: Anyone can vote instantly by sharing a link—no login required.

**Concurrent Processing**: Non-blocking vote submission using async/await for smooth performance.

**Live Results**: Beautiful, real-time charts showing vote counts and percentages.

**Vote Management**: Clear all votes with one click if needed.

**Optimized Images**: Automatic compression and resizing for fast loading.

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

3. Open your browser to `http://127.0.0.1:8000`.

## Usage

**Admin Panel**: Go to `/admin` to create and manage elections.

**Create Election**: Add a title and description, then add questions with optional images.

**Add Candidates**: For each question, add candidate names with optional bios and photos.

**Launch**: Click "Launch" to make the election active.

**Share**: Copy the voting link and share it with voters.

**Vote**: Voters access the link and vote instantly—no registration needed.

**Results**: View live results with charts and vote percentages.

**Clear Votes**: If needed, clear all votes from the admin panel.

## Technologies

- **Backend**: FastAPI with async/await
- **Database**: SQLAlchemy with SQLite
- **Images**: Pillow (automatic optimization)
- **Frontend**: Jinja2, Tailwind CSS, Chart.js
- **Storage**: Optimized JPEG files in `/static/uploads`
