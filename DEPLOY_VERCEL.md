# Deploying Transcript Formatter to Vercel

This guide will help you deploy the Transcript Formatter application to Vercel for public demo access.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com) if you don't have an account
2. **Vercel CLI** (optional): Install with `npm i -g vercel`
3. **Anthropic API Key**: Get your API key from [console.anthropic.com](https://console.anthropic.com)

## Deployment Steps

### Option 1: Deploy via GitHub (Recommended)

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Vercel deployment"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Connect to Vercel**:
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your GitHub repository
   - Vercel will auto-detect the configuration

3. **Add Environment Variables**:
   - In Vercel dashboard, go to Settings → Environment Variables
   - Add: `ANTHROPIC_API_KEY` with your API key value
   - Add: `FLASK_SECRET_KEY` with a secure random string

4. **Deploy**:
   - Click "Deploy"
   - Wait for the build to complete

### Option 2: Deploy via CLI

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel
   ```
   Follow the prompts and accept the defaults.

4. **Add Environment Variables**:
   ```bash
   vercel env add ANTHROPIC_API_KEY
   vercel env add FLASK_SECRET_KEY
   ```

5. **Redeploy with environment variables**:
   ```bash
   vercel --prod
   ```

## File Structure for Vercel

The deployment uses these key files:

- `vercel.json` - Configures Python runtime and routing
- `api/index.py` - Serverless function entry point
- `requirements.txt` - Python dependencies
- `.vercelignore` - Files to exclude from deployment

## Important Notes

### Serverless Limitations

- **Temporary Files**: Use `tempfile.TemporaryDirectory()` for file operations
- **No Persistent Storage**: Files are not saved between requests
- **Function Timeout**: Maximum 10 seconds for free tier, 60 seconds for Pro
- **Memory Limit**: 1024 MB for free tier

### Security Considerations

1. **API Key Security**:
   - Never commit your API key to the repository
   - Always use environment variables
   - Consider implementing rate limiting

2. **File Upload Security**:
   - Files are validated for type (.txt, .docx only)
   - Maximum file size is 16MB
   - Files are processed in temporary directories

3. **Public Access**:
   - Consider adding authentication if needed
   - Monitor usage to prevent abuse
   - Set up spending limits in Anthropic console

## Testing Your Deployment

Once deployed, your app will be available at:
- `https://your-app-name.vercel.app`

Test the deployment:
1. Visit the URL
2. Upload a sample transcript file
3. Click "Format Transcript"
4. Download the formatted document

## Troubleshooting

### "API Key not found" error
- Ensure `ANTHROPIC_API_KEY` is set in Vercel environment variables
- Redeploy after adding environment variables

### "Module not found" error
- Check that all dependencies are in `requirements.txt`
- Ensure the module structure is correct

### Large file errors
- Vercel has a 4.5MB request body limit
- Consider implementing chunked uploads for larger files

### Slow processing
- Cold starts can take 3-5 seconds
- Consider upgrading to Vercel Pro for better performance

## Monitoring

- View logs in Vercel dashboard under Functions tab
- Monitor API usage in Anthropic console
- Set up alerts for errors or high usage

## Custom Domain (Optional)

To add a custom domain:
1. Go to Settings → Domains in Vercel dashboard
2. Add your domain
3. Configure DNS as instructed

## Support

For issues specific to:
- Vercel deployment: [vercel.com/docs](https://vercel.com/docs)
- Anthropic API: [docs.anthropic.com](https://docs.anthropic.com)
- Application bugs: Create an issue in your GitHub repository