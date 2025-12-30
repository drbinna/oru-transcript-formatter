# ORU Transcript Formatting Application

A web application that uses **Claude AI** to intelligently format raw transcript text files into professionally styled Word documents.

**Live Demo:** [https://pmkdmqvn5v.us-east-2.awsapprunner.com](https://pmkdmqvn5v.us-east-2.awsapprunner.com)

## Features

- **AI-Powered Formatting** - Claude AI intelligently parses and formats transcripts
- **Template Learning** - Learns formatting rules from your sample document
- **Mixed Inline Formatting** - Bold speakers, italic quotes, bold scripture references
- **Instant Download** - Get formatted `.docx` files immediately

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, TypeScript, TailwindCSS |
| Backend | FastAPI (Python) |
| AI | Claude 3.5 Sonnet |
| Deployment | AWS App Runner |

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI endpoints
│   ├── formatter.py         # Claude AI formatting logic
│   └── requirements.txt
├── frontend/
│   ├── src/App.tsx          # React UI
│   └── public/              # Static assets
├── templates/
│   └── sample_formatted.docx
├── Dockerfile
└── apprunner.yaml
```

## Local Development

### Prerequisites
- Python 3.9+
- Node.js 18+
- Anthropic API key

### Setup

1. **Backend**
```bash
cd backend
cp .env.example .env  # Add your ANTHROPIC_API_KEY
pip install -r requirements.txt
uvicorn main:app --reload
```

2. **Frontend**
```bash
cd frontend
npm install
npm run dev
```

3. Open http://localhost:5173

## Deployment

Deploy to AWS App Runner:
```bash
./deploy-aws.sh
```

See `AWS_DEPLOY.md` for detailed instructions.

## License

MIT
