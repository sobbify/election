# Election Runner Clone (FastAPI)

A simple, secure, and shareable election management system built with Python FastAPI and vanilla HTML/CSS/JS.

## Features
- **Admin Dashboard**: Create elections, add questions/candidates, and manage voters.
- **Secure Voting**: Each voter gets a unique Voter ID and Voter Key.
- **Real-time Results**: Beautiful charts powered by Chart.js.
- **Single File Database**: Uses SQLite for easy sharing and local running.

## How to Run Locally

### 1. Install Dependencies
Make sure you have Python installed. Then run:
```bash
pip install -r requirements.txt
```

### 2. Start the Server
Run the FastAPI app using Uvicorn:
```bash
uvicorn main:app --reload
```

### 3. Access the App
- **User Interface**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Admin Dashboard**: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

## How to Use

1. **Create an Election**: Go to the Admin Dashboard and click "+ Create New Election".
2. **Setup Ballot**: Click "Manage" on your election. Add questions (positions) and candidates.
3. **Add Voters**: Add voter names/IDs. The system will generate a unique "Voter Key" for each.
4. **Launch**: Click "Launch Election" to make it active.
5. **Vote**: Share the link (e.g., `/vote/1`) with your voters. They will need their ID and Key to login and vote.
6. **Results**: Results are updated in real-time and can be viewed by the admin or voters after they vote.

## Sharing the Project
To share this project, simply zip the entire `election_app` folder. The `election.db` file contains all your election data, so you can even share a pre-configured election!

---
Built with ❤️ using FastAPI.
