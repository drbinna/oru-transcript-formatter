import { useState } from 'react'
import './App.css'

interface JobStatus {
  job_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at?: string
  started_at?: string
  completed_at?: string
  failed_at?: string
  error?: string
}

function App() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [_jobId, setJobId] = useState<string | null>(null)
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setError(null)
      setSuccess(false)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file')
      return
    }

    setLoading(true)
    setJobId(null)
    setJobStatus(null)
    setError(null)
    setSuccess(false)

    try {
      const formData = new FormData()
      formData.append('file', file)

      setJobStatus({ job_id: '', status: 'processing' })

      const response = await fetch('/api/format', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }))
        throw new Error(errorData.error || `Failed to format (${response.status})`)
      }

      // Download the returned .docx directly
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `formatted_${file.name.replace('.txt', '')}.docx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      setSuccess(true)
      setLoading(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      setLoading(false)
    }
  }

  return (
    <div
      className="min-h-screen"
      style={{
        backgroundImage: 'url(/oral_roberts.jpeg)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed'
      }}
    >
      {/* Dark overlay for readability */}
      <div className="min-h-screen" style={{ backgroundColor: 'rgba(0, 47, 96, 0.75)' }}>
        {/* Header */}
        <header className="bg-transparent">
          <div className="max-w-4xl mx-auto px-6 py-8 text-center">
            <img
              src="/oru_logo.png"
              alt="ORU Logo"
              className="h-20 mx-auto mb-4"
            />
            <h1 className="text-3xl font-bold tracking-tight">
              <span style={{ color: '#C5B783' }}>ORU</span>
              <span className="text-white"> Transcript Formatter</span>
            </h1>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-4xl mx-auto px-6 py-12">
          <div className="mb-8">
            <p className="text-white text-lg">
              Upload a raw transcript file and receive a professionally formatted Word document.
            </p>
          </div>

          {/* Upload Section */}
          <div className="bg-white border border-gray-200 rounded-lg p-8">
            <div
              className={`border-2 border-dashed rounded-lg p-10 text-center transition-colors ${file ? 'border-oru-gold bg-amber-50/30' : 'border-gray-300 hover:border-oru-gold'
                }`}
            >
              {!file ? (
                <div>
                  <div className="w-12 h-12 mx-auto mb-4 text-gray-400">
                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12l-3-3m0 0l-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                    </svg>
                  </div>
                  <label
                    htmlFor="file-upload"
                    className="cursor-pointer inline-block px-6 py-2.5 rounded font-medium transition-colors"
                    style={{ backgroundColor: '#002F60', color: '#FFFFFF' }}
                  >
                    Select transcript file
                  </label>
                  <input
                    id="file-upload"
                    type="file"
                    accept=".txt"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  <p className="mt-3 text-sm text-gray-500">
                    Supports only .txt files
                  </p>
                </div>
              ) : (
                <div>
                  <div className="w-12 h-12 mx-auto mb-4 text-oru-gold-dark">
                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p className="text-lg font-medium text-gray-900">{file.name}</p>
                  <p className="mt-1 text-sm text-gray-500">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                  <button
                    onClick={() => setFile(null)}
                    className="mt-3 text-sm text-gray-500 hover:text-red-600 transition-colors"
                  >
                    Remove file
                  </button>
                </div>
              )}
            </div>

            {/* Format Button */}
            {file && (
              <div className="mt-6">
                <button
                  onClick={handleUpload}
                  disabled={loading}
                  className="w-full py-3 rounded font-medium transition-all"
                  style={{
                    backgroundColor: loading ? '#D1D5DB' : '#002F60',
                    color: loading ? '#6B7280' : '#FFFFFF',
                    cursor: loading ? 'not-allowed' : 'pointer'
                  }}
                >
                  {loading ? 'Processing...' : 'Format Transcript'}
                </button>
              </div>
            )}

            {/* Progress */}
            {loading && jobStatus && (
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm text-gray-700">
                    {jobStatus.status === 'pending' && 'Starting...'}
                    {jobStatus.status === 'processing' && 'Formatting transcript...'}
                    {jobStatus.status === 'completed' && 'Complete'}
                  </span>
                  <span className="text-xs text-gray-500 uppercase tracking-wide">
                    {jobStatus.status}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div
                    className="h-1.5 rounded-full transition-all duration-500 bg-oru-gold-dark"
                    style={{
                      width: jobStatus.status === 'pending' ? '25%' :
                        jobStatus.status === 'processing' ? '60%' :
                          '100%'
                    }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-3">
                  {jobStatus.status === 'processing' && 'This typically takes 3-4 minutes'}
                  {jobStatus.status === 'pending' && 'Initializing AI formatter'}
                </p>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="mt-6 p-4 bg-red-50 border border-red-100 rounded-lg">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {/* Success */}
            {success && (
              <div className="mt-6 p-4 bg-green-50 border border-green-100 rounded-lg">
                <p className="text-sm text-green-700">
                  Transcript formatted successfully. Download started.
                </p>
              </div>
            )}
          </div>

          {/* Features */}
          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-3" style={{ backgroundColor: 'rgba(197, 183, 131, 0.2)' }}>
                <svg className="w-5 h-5" style={{ color: '#C5B783' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                </svg>
              </div>
              <h3 className="font-semibold text-white mb-1">Professional Output</h3>
              <p className="text-sm text-white/80">Formatted to ORU transcript standards</p>
            </div>

            <div>
              <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-3" style={{ backgroundColor: 'rgba(197, 183, 131, 0.2)' }}>
                <svg className="w-5 h-5" style={{ color: '#C5B783' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456z" />
                </svg>
              </div>
              <h3 className="font-semibold text-white mb-1">AI-Powered</h3>
              <p className="text-sm text-white/80">Claude AI handles intelligent formatting</p>
            </div>

            <div>
              <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-3" style={{ backgroundColor: 'rgba(197, 183, 131, 0.2)' }}>
                <svg className="w-5 h-5" style={{ color: '#C5B783' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                </svg>
              </div>
              <h3 className="font-semibold text-white mb-1">Instant Download</h3>
              <p className="text-sm text-white/80">Get your .docx file immediately</p>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="mt-16">
          <div className="max-w-4xl mx-auto px-6 py-6">
            <p className="text-sm text-white/70 text-center">
              Oral Roberts University - World Impact
            </p>
          </div>
        </footer>
      </div>
    </div>
  )
}

export default App
