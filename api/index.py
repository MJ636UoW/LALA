import os
import sys

# Ensure repository root is in sys.path for Vercel Serverless environment
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from main import app as fastapi_app

# Vercel entrypoint ASGI app reference
app = fastapi_app
