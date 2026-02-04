# LearnQuest Backend API 🚀

A Flask-based REST API for the LearnQuest Crowdsourced Learning Platform with Gamification.

## Team Members (Group 7)
- **Ibrahim Abdu** - Project Leader, Backend Architecture & Integration
- **Bradley Murimi** - Backend Developer (Auth & Gamification)
- **Julius Mutinda** - Frontend Developer (Auth & Learning)
- **Joyce Njogu** - Frontend Developer Lead (UI Components)
- **Ephrahim Otieno** - Full Stack Developer (Community Features)
- **Craig Omore** - Full Stack Developer (Admin & Creator)

## Features
- ✅ User Authentication (JWT-based)
- ✅ Role-based Access Control (Admin, Contributor, Learner)
- ✅ Learning Paths & Modules
- ✅ Resource Management
- ✅ Gamification (XP, Points, Badges, Achievements)
- ✅ Leaderboards & Challenges
- ✅ Comments & Discussions
- ✅ User Profiles & Progress Tracking

## Quick Start

### Prerequisites
- Python 3.8+ (or Python 3.14 with UV)
- pipenv or UV (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone git@github.com:MrNawir/LearnQuest-Backend.git
cd LearnQuest-Backend
```

2. Create and activate virtual environment:
```bash
# Using UV (recommended)
uv venv .venv
source .venv/bin/activate
uv pip install flask flask-sqlalchemy flask-migrate flask-cors flask-jwt-extended python-dotenv

# OR using pipenv
pipenv install
pipenv shell
```

3. Create a `.env` file:
```bash
cp .env.example .env
```

4. Initialize the database with seed data:
```bash
python seed.py
```

5. Run the application:
```bash
python run.py
```

The API will be available at `http://localhost:5000`

## Test Accounts

After running `seed.py`, the following test accounts are available:

| Role        | Email                  | Password    |
|-------------|------------------------|-------------|
| Admin       | admin@learnquest.com   | admin123    |
| Contributor | jane@learnquest.com    | teacher123  |
| Learner     | john@learnquest.com    | student123  |
| Learner     | alice@example.com      | alice123    |

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user (requires auth)

### Users
- `GET /api/users/` - Get all users
- `GET /api/users/<id>` - Get user by ID
- `PUT /api/users/profile` - Update profile (requires auth)
- `GET /api/users/<id>/stats` - Get user stats

### Learning Paths
- `GET /api/learning-paths/` - Get all published paths
- `GET /api/learning-paths/<id>` - Get path by ID
- `POST /api/learning-paths/` - Create path (contributors only)
- `POST /api/learning-paths/<id>/modules` - Add module
- `POST /api/learning-paths/<id>/rate` - Rate a path

### Resources
- `GET /api/resources/` - Get all resources
- `GET /api/resources/<id>` - Get resource by ID
- `POST /api/resources/<id>/rate` - Rate a resource

### Gamification
- `GET /api/gamification/badges` - Get all badges
- `GET /api/gamification/badges/<user_id>` - Get user's badges
- `GET /api/gamification/leaderboard` - Get leaderboard
- `GET /api/gamification/challenges` - Get challenges
- `GET /api/gamification/achievements` - Get achievements

## Tech Stack
- **Flask** - Web framework
- **Flask-SQLAlchemy** - Database ORM
- **Flask-Migrate** - Database migrations
- **Flask-JWT-Extended** - JWT authentication
- **Flask-CORS** - Cross-Origin Resource Sharing

## License
MIT
