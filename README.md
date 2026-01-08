# 📸 Simply Social — Image & Video Sharing Platform

A full‑stack image and video sharing application inspired by an Instagram‑style feed, built with FastAPI, SQLAlchemy (async), FastAPI‑Users, ImageKit, and a Streamlit frontend.

The project demonstrates production‑grade backend architecture, clean API versioning, authentication, media uploads, and a minimal but functional frontend client.


## Tech Stack
Backend: FastAPI, SQLAlchemy (async), FastAPI Users  
Frontend: Streamlit  
Media: ImageKit  
Auth: JWT  
Infra: uv, uv.lock


## 📰 Features:

### Authentication & Users

- JWT‑based authentication using FastAPI‑Users
- User registration, login, logout
- Password reset & verification endpoints
- Versioned auth routes (/api/v1/auth)

### Media & Posts

- Upload images or videos
- Automatic upload to ImageKit
- Supports captions
- Owner‑only delete functionality
- Media metadata stored in database

### Feed

- Global feed ordered by newest posts
- Authenticated access
- Includes owner flag for UI actions
- Designed for future pagination

### Backend Architecture

- Async FastAPI application
- Async SQLAlchemy ORM
- Centralized dependency injection
- Structured logging system
- Application lifespan for startup/shutdown
- Environment‑driven configuration

### Frontend

- Streamlit‑based UI
- Login & signup flows
- Upload page
- Feed page with delete controls
- Caption overlay rendering via ImageKit transforms


## 📂 Project Structure

```
.
├── src/
│ └── VideoSharingApp/
│ ├── app.py                # FastAPI app wiring
│ ├── database.py           # ORM models & DB session
│ ├── images.py             # ImageKit client
│ ├── users.py              # Auth & user management
│ ├── schemas.py            # API schemas
│ ├── constants/
│ │ └── auth.py             # Versioned auth paths
│ ├── core/
│ │ ├── dependencies.py     # Shared dependencies
│ │ └── lifespan.py         # App startup/shutdown
│ ├── routers/
│ │ ├── health.py           # Health check
│ │ └── v1/
│ │ ├── feed.py             # Feed API
│ │ └── posts.py            # Post APIs
│ └── utils/
│ └── logger.py             # Logging setup
├── frontend.py             # Streamlit frontend
├── main.py                 # Application entrypoint
├── pyproject.toml
├── uv.lock
└── README.md
```


## 🚀 Getting Started

**1. Clone the Repository**
```
git clone https://github.com/Vish501/Video-Sharing-Application.git
cd Video-Sharing-Application
```

**2. Setup Virtual Environment**
Create a `.env` file in the project root:
```
# Application
HOST=0.0.0.0
PORT=8000
APPLICATION_RELOAD=true

# Database
DATABASE_DIR=./artifacts/database

# Auth
JWT_SECRET_TOKEN=your-secret-key

# ImageKit
IMAGEKIT_PRIVATE_KEY=your-imagekit-private-key
```

**3. Install Dependencies**
Using uv:
```
uv sync
```

**4. Run the Backend**
```
uv run main.py
```

API will be available at: `http://localhost:8000`

**4. Run the Frontend**
In a separate terminal:
```
streamlit run frontend.py
```


## API Overview

**Health Check**
```
GET /health
```

**Auth (v1)**
```
POST /api/v1/auth/register
POST /api/v1/auth/jwt/login
POST /api/v1/auth/jwt/refresh
POST /api/v1/auth/jwt/logout
```

**Feed**
```
GET /api/v1/feed
```
Returns a list of recent posts (authenticated).

**Posts**
```
POST /api/v1/posts/upload
DELETE /api/v1/posts/{post_id}
```


## 🧠 Design Decisions

- Versioned APIs (`/api/v1`) to allow safe evolution
- Centralized auth paths to avoid hard‑coding URLs
- Async everywhere for scalability
- Fail‑fast startup via lifespan events
- Lockfile committed for reproducible builds
- Frontend kept simple to showcase backend capabilities


## Future Improvements

- Pagination & infinite scroll
- Likes and comments
- User profiles
- Role‑based permissions
- Production‑grade deployment (Docker + Gunicorn)
- Object storage abstraction


## 🙋‍♂️ Author

This project was developed and is maintained by **Vish501** - an AI Egineer, with experience spanning finance and applied machine learning, building end-to-end systems that bridge product thinking and scalable backend engineering.

Feel free to contribute to this project by submitting issues or pull requests. For any questions or suggestions, please contact Vish501.