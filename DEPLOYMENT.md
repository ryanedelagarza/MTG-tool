# 🚀 Deploying to Streamlit Cloud

## Quick Deployment Steps

### 1. Push to GitHub
Your code is already on GitHub at: https://github.com/ryanedelagarza/MTG-tool

### 2. Deploy on Streamlit Cloud

1. Go to: https://share.streamlit.io/
2. Sign in with your GitHub account
3. Click **"New app"**
4. Configure your app:
   - **Repository**: `ryanedelagarza/MTG-tool`
   - **Branch**: `main`
   - **Main file path**: `app.py`

### 3. Configure Secrets

Click **"Advanced settings"** before deploying, then add your secrets:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
```

**Important**: Replace `your_gemini_api_key_here` with your actual Gemini API key.

### 4. Deploy!

Click **"Deploy"** and wait for the app to build (usually 2-3 minutes).

## 🔧 Troubleshooting

### "Error running app"
- **Check secrets**: Make sure `GEMINI_API_KEY` is set in Streamlit Cloud secrets
- **Check logs**: Click on "Manage app" → "Logs" to see detailed error messages
- **Dependencies**: Ensure all packages in `requirements.txt` are compatible

### API Key Issues
If you see "GEMINI_API_KEY not found":
1. Go to your app dashboard
2. Click **⋮** (three dots) → **Settings**
3. Go to **Secrets** section
4. Add your API key in TOML format:
   ```toml
   GEMINI_API_KEY = "your_key_here"
   ```
5. Click **Save**
6. The app will automatically restart

### File Upload Issues
- Streamlit Cloud has upload limits (200MB per file)
- Large CSV files may need to be compressed or split

### Performance Issues
- Free tier has resource limits
- Consider optimizing large operations
- Add loading indicators for long-running tasks

## 🔄 Updating Your Deployed App

After pushing changes to GitHub:
1. Streamlit Cloud will automatically detect changes
2. The app will rebuild and redeploy (usually takes 2-3 minutes)
3. You can manually trigger a reboot from the app dashboard

## 📱 Sharing Your App

Once deployed, your app will be available at:
```
https://your-app-name.streamlit.app
```

You can:
- Share this URL with anyone
- Customize the subdomain in app settings
- Add password protection (requires Streamlit Teams plan)

## 💡 Best Practices

### Security
- ✅ Never commit API keys to GitHub
- ✅ Use Streamlit secrets for sensitive data
- ✅ Keep your `.env` file in `.gitignore`

### Performance
- Optimize large data operations
- Use `@st.cache_data` for expensive computations
- Minimize API calls where possible

### User Experience
- Add loading indicators
- Provide clear error messages
- Include help documentation

## 🆘 Getting Help

If you encounter issues:
1. Check the [Streamlit docs](https://docs.streamlit.io/)
2. Visit the [Streamlit forums](https://discuss.streamlit.io/)
3. Check the app logs in your Streamlit Cloud dashboard
4. Review the [GitHub repository](https://github.com/ryanedelagarza/MTG-tool)

## 📊 Monitoring

Access your app dashboard to monitor:
- App usage and analytics
- Error logs and debugging info
- Resource usage
- Deployment history

---

**Note**: This app uses the Google Gemini API, which has its own rate limits and quotas. Monitor your API usage at: https://ai.google.dev/

