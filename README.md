# FIFA World Cup 2026 Tracker

A robust full-stack web application built to seamlessly track the 2026 FIFA World Cup format. Featuring a dynamic 48-team dashboard, the application offers live match score updates, complex group standings calculations (including the intricate 3rd-place tie-breakers), and a fully automated real-time 32-team knockout bracket visualization.

## 🚀 Features

- **Automated Live Score Syncing**: The backend features a specialized sync script that dynamically tracks live matches and updates scores in real-time by polling the football-data.org API.
- **Complex Standings Engine**: The sorting engine calculates group rankings based on points, goal differences, and goals scored. Crucially, it manages the complex "best third-place" calculations required for the new 48-team tournament structure.
- **Dynamic Knockout Bracket**: As group stages and subsequent knockout rounds conclude, the interactive 32-team bracket is automatically populated with the advancing teams, managing all intricate routing paths algorithmically.
- **Unified Match Calendar**: A comprehensive Match Calendar groups all 104 matches by day and time, correctly unifying the UI presentation for raw matches and enriched knockout mappings.
- **Resilient Database Architecture**: Powered by SQLAlchemy with robust connection pooling to handle idle serverless database disconnections (e.g., Neon Postgres) gracefully.

## 🏗️ Architecture

The project employs a modern, decoupled architecture:

- **Frontend (`/frontend`)**: Built with **Angular**, featuring a dynamic and responsive component-driven dashboard. Highlights include real-time Angular Signals for state management, an interactive bracket, grouped Match Calendar, and dynamic standings tables.
- **Backend (`/backend`)**: Built with **Python (FastAPI)**. Interfaces with a **PostgreSQL (Neon)** database via **SQLAlchemy** to store all match, team, and standings data. 
- **Data Engine**: The backend leverages a scheduled cron loop (`scheduler.py`) to periodically hit the `/matches/sync-live` endpoints, automatically pulling live API data and algorithmically updating the bracket tree progression logic in `main.py`.

## ⚙️ Local Setup

### Prerequisites
- Node.js (v18+) & npm (for Frontend)
- Python 3.10+ (for Backend)
- PostgreSQL Database URI (e.g., Neon DB)
- [Football-Data.org](https://www.football-data.org/) API Key

### Backend
1. Navigate to `cd backend`
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file:
   ```env
   DATABASE_URL=postgresql://user:password@host/dbname
   SPORTS_API_KEY=your_football_data_api_key
   ```
5. Run the FastAPI development server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend
1. Navigate to `cd frontend`
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the Angular server:
   ```bash
   npm start
   ```
4. Access the dashboard at `http://localhost:4200`

## 🌍 Deployment

- **Backend (API)**: Designed to be deployed on **Render** (Web Service) using the `uvicorn` entry point. Ensure environment variables are configured in the Render dashboard.
- **Frontend (UI)**: Can be deployed on **Render** (Static Site), **Vercel**, or **Netlify** using the `npm run build` command, pointing the build directory to `dist/frontend`.
