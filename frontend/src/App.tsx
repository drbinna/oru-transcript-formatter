import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [isDragging, setIsDragging] = useState(false)

  const handleFileChange = (selectedFile: File | null) => {
    if (!selectedFile) return
    if (!selectedFile.name.toLowerCase().endsWith('.txt')) {
      setError('Please select a .txt file')
      return
    }
    setFile(selectedFile)
    setError(null)
    setSuccess(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const dropped = e.dataTransfer.files[0]
    handleFileChange(dropped)
  }

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    setSuccess(false)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('/api/format', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }))
        throw new Error(errorData.error || `Error ${response.status}`)
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = file.name.replace('.txt', '_summary.docx')
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      setSuccess(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <div className="container">
        <header>
          <div className="icon">📄</div>
          <h1>Transcript Summarizer</h1>
          <p>Upload a <code>.txt</code> transcript and get a clean summary document in seconds.</p>
        </header>

        <main>
          <div
            className={`dropzone ${isDragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-input')?.click()}
          >
            <input
              id="file-input"
              type="file"
              accept=".txt"
              onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
              style={{ display: 'none' }}
            />
            {file ? (
              <div className="file-info">
                <span className="file-icon">✓</span>
                <span className="file-name">{file.name}</span>
                <span className="file-size">{(file.size / 1024).toFixed(1)} KB</span>
                <button
                  className="remove-btn"
                  onClick={(e) => { e.stopPropagation(); setFile(null); setSuccess(false) }}
                >
                  Remove
                </button>
              </div>
            ) : (
              <div className="upload-prompt">
                <span className="upload-icon">⬆</span>
                <span>Drop your .txt file here, or <strong>click to browse</strong></span>
              </div>
            )}
          </div>

          {file && !loading && !success && (
            <button className="submit-btn" onClick={handleUpload}>
              Summarize Transcript
            </button>
          )}

          {loading && (
            <div className="status processing">
              <div className="spinner"></div>
              <span>Summarizing your transcript…</span>
            </div>
          )}

          {error && (
            <div className="status error">
              ⚠ {error}
            </div>
          )}

          {success && (
            <div className="status success">
              <span>✓ Summary downloaded successfully!</span>
              <button className="reset-btn" onClick={() => { setFile(null); setSuccess(false) }}>
                Summarize another
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default App
