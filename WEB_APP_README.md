# 🎓 ORU Transcript Formatter

AI-powered transcript formatting tool for Oral Roberts University with professional web interface and CLI support.

## ✨ Features

### 🤖 **AI-Powered Formatting**
- **Claude AI Integration** - Intelligent transcript processing
- **Real-time Progress** - Live updates during processing

### 🎨 **Modern Design**
- **ORU Brand Colors** - Official university color scheme
- **Responsive Layout** - Works on desktop, tablet, and mobile
- **Drag & Drop Upload** - Intuitive file handling
- **Professional Output** - Clean, formatted Word documents

### 📝 **Smart Processing**
- **Speaker Detection** - Automatically identifies and formats speakers
- **Scripture References** - Detects and highlights Bible verses
- **Character Encoding** - Fixes common text encoding issues
- **Paragraph Structure** - Creates natural, readable flow

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Web Application
```bash
python start_web_app.py
```

### 3. Access the Interface
Open your browser and go to: **http://localhost:5000**

## 🎯 How to Use

1. **Upload File** - Drag and drop or click to select a `.txt` or `.docx` transcript file
2. **Process** - Click "Format Transcript" to begin processing with Claude AI
3. **Download** - Get your professionally formatted Word document

## 🎨 Design Features

### Color Scheme (ORU Brand)
- **Primary Blue**: `#003366` - Main brand color
- **Gold Accent**: `#FFD700` - Highlighting and CTAs
- **Light Blue**: `#4A90E2` - Interactive elements
- **Clean White**: `#FFFFFF` - Content backgrounds

### UI Components
- **Gradient Backgrounds** - Modern visual appeal
- **Smooth Animations** - Professional interactions
- **Progress Indicators** - Real-time feedback
- **Responsive Grid** - Feature showcase

## 📁 File Structure

```
transcript-formatter/
├── web_app.py              # Flask application
├── start_web_app.py        # Startup script
├── templates/
│   └── index.html          # Main web interface
├── uploads/                # Temporary file storage
├── outputs/                # Processed documents
└── requirements.txt        # Dependencies
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file with:
```
ANTHROPIC_API_KEY=your_claude_api_key_here
```

### Flask Settings
- **Max File Size**: 16MB
- **Allowed Extensions**: `.txt`, `.docx`
- **Debug Mode**: Enabled for development

## 🌟 Key Features Showcase

### 1. **Intelligent Upload Area**
- Drag and drop functionality
- Visual feedback on file selection
- File type validation

### 2. **Processing Options**
- Claude AI formatter with intelligent formatting
- Clear status updates during processing

### 3. **Real-time Progress**
- Animated progress bar
- Status updates
- Professional loading states

### 4. **Results Display**
- Success confirmation
- Download button
- Content preview
- Formatter information

## 🎓 ORU Integration

The web application features:
- **Official ORU Colors** - Brand-compliant design
- **University Branding** - ORU logo and identity
- **Professional Appearance** - Suitable for academic use
- **Accessibility** - Modern web standards

## 🔒 Security Features

- **File Type Validation** - Only allows safe file types
- **Secure Filenames** - Prevents directory traversal
- **Temporary Storage** - Files cleaned up after processing
- **Environment Variables** - Secure API key handling

## 📱 Responsive Design

The interface adapts to:
- **Desktop** - Full feature set
- **Tablet** - Optimized layout
- **Mobile** - Touch-friendly interface

## 🚀 Production Deployment

For production use:
1. Change the Flask secret key
2. Set `debug=False`
3. Use a production WSGI server (gunicorn, uWSGI)
4. Configure proper file storage
5. Add authentication if needed

## 🎉 Ready to Use!

Your ORU Transcript Formatter web application is ready to provide a professional, AI-powered transcript formatting experience with a beautiful, brand-compliant interface!