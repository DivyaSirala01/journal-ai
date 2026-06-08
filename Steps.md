How to run

Terminal 1 — backend (from project root):
uvicorn main:app --reload

Terminal 2 — frontend:
cd frontend
npm run dev


Open http://localhost:5173. Vite proxies /notes and /query to the API on port 8000, so no backend CORS changes are needed.

