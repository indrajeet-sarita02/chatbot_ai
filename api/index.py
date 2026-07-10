def handler(event, context):
    return {
        "statusCode": 200,
        "headers": {"content-type": "text/html"},
        "body": """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>ShopEase AI Assistant</title></head>
<body style="font-family:sans-serif;text-align:center;padding:40px">
  <h1>🛍️ ShopEase AI Assistant</h1>
  <p>This is a Streamlit app. Deploy it on Streamlit Community Cloud:</p>
  <ol style="text-align:left;display:inline-block">
    <li>Go to <a href="https://streamlit.io/cloud">streamlit.io/cloud</a></li>
    <li>Sign in with GitHub</li>
    <li>Click "New app" → select this repo</li>
    <li>Set main file: <code>app.py</code></li>
    <li>Deploy!</li>
  </ol>
  <hr>
  <p><small>Python • LangChain • LangGraph • SQLite • Streamlit</small></p>
</body>
</html>"""
    }
