# Transcript Summarizer

A web application that uses **Claude AI** to instantly summarize raw `.txt` transcript files into clean, structured Word documents.

**Live:** [https://oru-transcript-formatter-cvu0-nghnc7qkt.vercel.app](https://oru-transcript-formatter-cvu0-nghnc7qkt.vercel.app)

## Features

- **Single API call** — no chunking, no polling, results in ~10 seconds
- **Structured output** — Title, Overview, Key Points, Main Discussion, Action Items
- **Drag & drop** upload with instant `.docx` download
- **Serverless** — deployed on Vercel with zero infrastructure to manage

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, TypeScript, Vite |
| Backend | Python (Vercel Serverless) |
| AI | Claude Haiku |
| Deployment | Vercel |

## Project Structure

```
├── api/
│   └── format.py          # Vercel Python serverless handler
├── backend/
│   ├── formatter.py       # Claude summarization logic
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx        # React UI
│   │   └── App.css        # Styles
│   └── index.html
├── requirements.txt       # Root-level deps (for Vercel)
└── vercel.json            # Vercel deployment config
```

## Local Development

**Prerequisites:** Python 3.11+, Node.js 18+, Anthropic API key

**Backend**
```bash
cd backend
cp .env.example .env      # Add your ANTHROPIC_API_KEY
pip install -r requirements.txt
uvicorn main:app --reload  # Runs on http://localhost:8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev               # Runs on http://localhost:5173
```

## Deployment (Vercel)

1. Push your repo to GitHub
2. Import the project at [vercel.com/new](https://vercel.com/new)
3. Add environment variable: `ANTHROPIC_API_KEY` = your key
4. Click **Deploy** — Vercel handles everything else

The `vercel.json` configures the build automatically:
- Frontend: built with Vite, served as static files
- Backend: `api/format.py` runs as a Python serverless function

## License

MIT
