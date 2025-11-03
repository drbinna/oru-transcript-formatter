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
  const [jobId, setJobId] = useState<string | null>(null)
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

      // Use relative path in production, absolute in development
      const baseUrl = import.meta.env.PROD 
        ? '' 
        : 'http://localhost:8000'
      
      // Step 1: Submit job and get job ID
      const response = await fetch(`${baseUrl}/format`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Unknown error')
        throw new Error(`Failed to start formatting (${response.status}): ${errorText}`)
      }

      const jobData = await response.json()
      const newJobId = jobData.job_id
      setJobId(newJobId)
      setJobStatus({
        job_id: newJobId,
        status: jobData.status
      })

      // Step 2: Poll for job status
      const pollStatus = async (): Promise<void> => {
        const statusResponse = await fetch(`${baseUrl}/format/${newJobId}/status`)
        
        if (!statusResponse.ok) {
          throw new Error(`Failed to check status: ${statusResponse.status}`)
        }

        const status: JobStatus = await statusResponse.json()
        setJobStatus(status)

        if (status.status === 'completed') {
          // Step 3: Download the file
          const downloadResponse = await fetch(`${baseUrl}/format/${newJobId}/download`)
          
          if (!downloadResponse.ok) {
            throw new Error(`Failed to download: ${downloadResponse.status}`)
          }

          const blob = await downloadResponse.blob()
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
        } else if (status.status === 'failed') {
          throw new Error(status.error || 'Processing failed')
        } else {
          // Still processing, poll again in 3 seconds
          setTimeout(pollStatus, 3000)
        }
      }

      // Start polling after 2 seconds
      setTimeout(pollStatus, 2000)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            ORU Transcript Formatter
          </h1>
          <p className="text-lg text-gray-600">
            Upload your raw transcript and get a professionally formatted Word document
          </p>
        </div>

        {/* Upload Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
            {!file ? (
              <div>
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 48 48"
                >
                  <path
                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-4h12m-4 4v12m0 0l-4-4m4 4l4-4"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                <div className="mt-4">
                  <label
                    htmlFor="file-upload"
                    className="cursor-pointer bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold inline-block transition-colors"
                  >
                    Select a transcript file
                  </label>
                  <input
                    id="file-upload"
                    type="file"
                    accept=".txt"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  <p className="mt-2 text-sm text-gray-500">
                    Choose a .txt file to format
                  </p>
                </div>
              </div>
            ) : (
              <div>
                <svg
                  className="mx-auto h-12 w-12 text-green-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <p className="mt-4 text-lg font-semibold text-gray-900">
                  {file.name}
                </p>
                <p className="mt-2 text-sm text-gray-500">
                  {(file.size / 1024).toFixed(2)} KB
                </p>
                <button
                  onClick={() => setFile(null)}
                  className="mt-4 text-sm text-red-600 hover:text-red-700"
                >
                  Remove
                </button>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          {file && (
            <div className="mt-6 flex gap-4">
              <button
                onClick={handleUpload}
                disabled={loading}
                className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-all ${
                  loading
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
              >
                {loading ? 'Formatting...' : 'Format & Download'}
              </button>
            </div>
          )}

          {/* Job Status */}
          {loading && jobStatus && (
            <div className="mt-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  {jobStatus.status === 'pending' && '⏳ Job submitted, starting processing...'}
                  {jobStatus.status === 'processing' && '⚙️ Processing transcript...'}
                  {jobStatus.status === 'completed' && '✅ Processing complete!'}
                </span>
                <span className="text-sm font-medium text-blue-600">
                  {jobStatus.status === 'pending' && 'Pending'}
                  {jobStatus.status === 'processing' && 'Processing'}
                  {jobStatus.status === 'completed' && 'Complete'}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className={`h-3 rounded-full transition-all duration-300 ease-out ${
                    jobStatus.status === 'pending' ? 'bg-yellow-500 w-1/3' :
                    jobStatus.status === 'processing' ? 'bg-blue-600 animate-pulse' :
                    'bg-green-600'
                  }`}
                  style={{ 
                    width: jobStatus.status === 'pending' ? '33%' :
                           jobStatus.status === 'processing' ? '66%' :
                           '100%'
                  }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                {jobStatus.status === 'processing' && 'This typically takes 3-4 minutes. The page will auto-refresh...'}
                {jobStatus.status === 'pending' && 'Initializing...'}
                {jobStatus.status === 'completed' && 'Download should start automatically!'}
              </p>
              {jobId && (
                <p className="text-xs text-gray-400 mt-1">Job ID: {jobId.slice(0, 8)}...</p>
              )}
            </div>
          )}

          {/* Messages */}
          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {success && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-800">
                ✅ Transcript formatted successfully! Download started.
              </p>
            </div>
          )}
        </div>

        {/* Features */}
        <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Professional Formatting</h3>
            <p className="text-sm text-gray-600">Industry-standard transcript layout</p>
          </div>

          <div className="text-center">
            <div className="bg-indigo-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">AI-Powered</h3>
            <p className="text-sm text-gray-600">Claude AI ensures perfect readability</p>
          </div>

          <div className="text-center">
            <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.121 14.121L19 19m-7-7l7-7m-7 7l-2.879 2.879M12 12L9.121 9.121m6.364-6.364L19 5m-7-7l2.879 2.879M5 19l2.879-2.879m0 0L5 13.121m2.879 2.879L13.121 19M9.121 9.121l-2.879 2.879" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">ORU Branding</h3>
            <p className="text-sm text-gray-600">Preserves World Impact branding</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App