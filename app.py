"""
Compatibility shim that:
- Re-exports `app`, `db`, `User`, `Task` for tests importing `from app import ...`.
- Starts the development server when executed directly: `python app.py`.
"""

import os
from flask_backend import app, db, User, Task  # noqa: F401


if __name__ == "__main__":
    # Ensure tables exist, then run the dev server
    with app.app_context():
        db.create_all()
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    app.run(debug=True, host=host, port=port)
