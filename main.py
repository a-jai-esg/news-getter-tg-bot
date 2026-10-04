import sys

from dotenv import load_dotenv
from quart import Quart
from quart_cors import cors

load_dotenv()

app = Quart(__name__)
app = cors(app, allow_origin="*")

# Target Host URLs and Mode
SYSTEM_MODE = os.environ.get("MODE") # "production" or "development"

# Register blueprints
from controllers.news_controller import news_controller
app.register_blueprint(news_controller, url_prefix="/news")

if __name__ == "__main__":
    # Local development only.
    # Production: gunicorn main:app (see gunicorn.conf.py)
    try:
        app.run(debug=True, host="127.0.0.1" if SYSTEM_MODE.strip().lower() == "development" else "0.0.0.0", port=5000)
        print("News API catcher is running.")
    except Exception as e:
        sys.stderr.write(f"News API catcher failed to start: {e}\n")
