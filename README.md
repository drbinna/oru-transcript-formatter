# Transcript Summarizer

Upload a raw `.txt` meeting or video transcript and get back a clean, structured Word document in a few seconds.

**Live:** https://oru-transcript-formatter-cvu0.vercel.app/

## How it works

1. The React frontend posts the `.txt` file to `/api/format`.
2. A Python serverless function sends the transcript to **Fireworks AI** (DeepSeek V4 Flash by default) with a fixed summarization prompt.
3. The model's response is parsed into sections and rendered as a `.docx`, which streams straight back to the browser as a download.

One API call, no chunking, no polling. Typical turnaround is 4–8 seconds.

## Output structure

Every summary follows the same layout:

- **Title**
- **Overview** — 2–3 sentence summary
- **Key Points** — bulleted list
- **Main Discussion** — 3–5 paragraphs of prose
- **Action Items** — bulleted, or "None identified"

## Tech stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, Vite |
| API | Python 3.12, Vercel Serverless Functions |
| AI | Fireworks AI via the OpenAI-compatible endpoint (`openai` SDK) |
| Documents | `python-docx` |
| Hosting | Vercel |

## Project structure

```
├── api/
│   └── format.py          # Vercel serverless handler: validates upload, returns .docx
├── backend/
│   ├── formatter.py       # Prompt, Fireworks call, docx builder
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx        # Upload UI
│   │   └── App.css
│   └── index.html
├── requirements.txt       # Python deps installed by Vercel
└── vercel.json            # Build config + /api rewrite
```

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FIREWORKS_API_KEY` | Yes | — | Get one at [fireworks.ai](https://fireworks.ai/account/api-keys) |
| `FIREWORKS_MODEL` | No | `accounts/fireworks/models/deepseek-v4-flash-0731` | Any Fireworks serverless chat model |

To switch models, set `FIREWORKS_MODEL` to another ID from the [Fireworks model library](https://app.fireworks.ai/models?filter=LLM&serverless=true). Models that follow structured instructions well (DeepSeek, GLM, Kimi) work best because the docx builder keys off the section headers.

## API

`POST /api/format` — multipart form with a single `file` field (`.txt`, UTF-8).

- **200** — `.docx` bytes, `Content-Disposition: attachment`
- **400** — missing/empty/non-`.txt` file
- **503** — summarizer unavailable (bad key, rate limit, provider outage). Body: `{"error": "<user-safe message>"}`
- **500** — unexpected error

Transcripts over ~80,000 characters are truncated before summarizing.

```bash
curl -F "file=@meeting.txt" https://oru-transcript-formatter-cvu0.vercel.app/api/format -o summary.docx
```

## Local development

**Prerequisites:** Node.js 18+, Python 3.11+, the [Vercel CLI](https://vercel.com/docs/cli), a Fireworks API key.

```bash
cp backend/.env.example .env        # add FIREWORKS_API_KEY
cd frontend && npm install && cd ..
vercel dev                           # serves the frontend and /api together
```

`vercel dev` runs the Python function locally the same way it runs in production, so the upload flow works end to end at http://localhost:3000.

To exercise the summarizer directly without the web layer:

```bash
pip install -r requirements.txt
cd backend
FIREWORKS_API_KEY=... python -c "from formatter import format_transcript; open('out.docx','wb').write(format_transcript(open('sample.txt').read()))"
```

## Deployment

The project is linked to Vercel; every push to `main` deploys automatically.

For a fresh deployment:

1. Import the repo at [vercel.com/new](https://vercel.com/new)
2. Add the `FIREWORKS_API_KEY` environment variable
3. Deploy — `vercel.json` handles the Vite build and the Python function

Environment variable changes only take effect on the next deployment, so redeploy after editing them.

## License

MIT
