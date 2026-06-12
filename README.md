# FIFA World Cup 2026 Tracker

A full-stack web application designed to track the 2026 FIFA World Cup. This application features live match score updates, dynamic bracket generation, and real-time tournament standings logic (including complex 3rd-place tie-breaker resolution).

## Architecture

The project is split into two main components:

- **Frontend (`/frontend`)**: Built with Angular, providing a dynamic, responsive dashboard. It displays the calendar of matches, group standings, top third-place teams, and an interactive 32-team knockout bracket.
- **Backend (`/backend`)**: Built with Python (FastAPI). It interfaces with a PostgreSQL database (Neon) to store tournament data, manages complex sorting logic for standings, and automatically fetches live data via background cron jobs.

## Features

- **Live Score Syncing**: A background scheduler dynamically tracks live matches and updates scores in real-time by polling the football-data.org API.
- **Complex Standings Engine**: Calculates group rankings based on points, goal difference, goals scored, and handles the intricate "best third-place" calculations required for the 48-team 2026 World Cup format.
- **Automated Knockout Bracket**: As group stages conclude, the bracket is automatically populated with the advancing teams, including the complex routing of third-place qualifiers.
- **Database Architecture**: Powered by SQLAlchemy with robust connection pooling to handle idle serverless database disconnections gracefully.

## Getting Started

### Prerequisites
- Node.js & npm (for Frontend)
- Python 3.10+ (for Backend)
- PostgreSQL Database
- [Football-Data.org](https://www.football-data.org/) API Key

### Backend Setup
1. Navigate to the `backend` directory.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the `backend` directory and provide:
   ```env
   DATABASE_URL=postgresql://user:password@host/dbname
   SPORTS_API_KEY=your_football_data_api_key
   ```
4. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup
1. Navigate to the `frontend` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the Angular development server:
   ```bash
   ng serve
   ```
4. Open your browser and navigate to `http://localhost:4200`.

## Deployment

This application is configured for deployment on modern PaaS platforms:
- **Backend**: Can be deployed on platforms like Render or Heroku. Ensure environment variables (`DATABASE_URL`, `SPORTS_API_KEY`) are set.
- **Frontend**: Can be built into static assets (`ng build`) and deployed to services like Vercel, Netlify, or Render static sites.
