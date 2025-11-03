# 🧪 Local Testing Guide

This guide will help you test the ORU Transcript Formatting Application locally on your machine.

## Prerequisites

✅ **Python 3.9+** - You have Python 3.13.5  
✅ **Node.js** - You have Node v22.17.0  
⚠️ **Anthropic API Key** - You'll need to set this up (see below)

---

## Quick Start

### Step 1: Set Up Backend Environment

1. **Create a `.env` file in the `backend/` directory:**

```bash
cd backend
touch .env
```

2. **Add your Anthropic API key to the `.env` file:**

Open `backend/.env` and add:
```
ANTHROPIC_API_KEY=your-api-key-here
```

Replace `your-api-key-here` with your actual Anthropic API key.  
[Get your API key here](https://console.anthropic.com/)

### Step 2: Install Backend Dependencies

```bash
cd backend
pip3 install -r requirements.txt
```

### Step 3: Install Frontend Dependencies

```bash
cd frontend
npm install
```

---

## Running the Application

You'll need to run both the backend and frontend in separate terminal windows.

### Terminal 1: Backend Server

```bash
cd backend
uvicorn main:app --reload
```

The backend will start at: **http://localhost:8000**

You can verify it's working by visiting: http://localhost:8000/api

### Terminal 2: Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will start at: **http://localhost:5173**

---

## Testing the Application

1. **Open your browser** and navigate to: http://localhost:5173

2. **Test with a sample file:**
   - A sample transcript is available at: `samples/WI0110-2448_-_Last_Days.txt`
   - Click "Select a transcript file" and choose this file
   - Click "Format & Download"
   - The formatted `.docx` file should download automatically

3. **Check the backend logs** in Terminal 1 to see processing details

---

## Troubleshooting

### Backend Issues

**Error: ANTHROPIC_API_KEY not found**
- Make sure you created `backend/.env` with your API key
- Verify the file is in the `backend/` directory (not the root)

**Error: Module not found**
- Run `pip3 install -r requirements.txt` again in the backend directory
- Make sure you're using Python 3.9+

**Port 8000 already in use**
- Stop any other process using port 8000, or change the port:
  ```bash
  uvicorn main:app --reload --port 8001
  ```
- Update the frontend API URL in `App.tsx` if you change the port

### Frontend Issues

**Connection refused errors**
- Make sure the backend is running on port 8000
- Check the backend terminal for errors

**npm install fails**
- Try clearing the cache: `npm cache clean --force`
- Delete `node_modules` and `package-lock.json`, then run `npm install` again

**Port 5173 already in use**
- Vite will automatically try the next available port, or you can specify:
  ```bash
  npm run dev -- --port 5174
  ```

---

## API Testing (Optional)

You can also test the backend API directly using curl:

```bash
curl -X POST http://localhost:8000/format \
  -F "file=@samples/WI0110-2448_-_Last_Days.txt" \
  --output test_output.docx
```

---

## What to Expect

1. **Upload time**: The formatting process takes 2-3 minutes as it uses Claude AI
2. **Progress bar**: You'll see a progress indicator in the frontend
3. **Download**: The formatted `.docx` file will automatically download when ready
4. **Formatting**: The output will match the template in `templates/sample_formatted.docx`

---

## Next Steps

Once everything is working:
- Try with your own transcript files
- Check the formatted output against the template
- Review backend logs for any issues

---

## Development Notes

- Backend uses FastAPI with CORS enabled for local development
- Frontend uses Vite with proxy configuration for API calls
- Template file location is automatically detected from multiple possible paths
- Formatting requests are serialized to avoid API rate limits

