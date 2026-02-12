# LearnQuest Backend API

A Flask-based REST API for the LearnQuest Crowdsourced Learning Platform with Gamification.

## Team Members — Group 7
- **Ibrahim Abdu** — Project Leader, Backend Architecture & Integration
- **Bradley Murimi** — Backend Developer Lead (Auth & Gamification)
- **Joyce Njogu** — Frontend Developer Lead
- **Julius Mutinda** — Frontend Developer (Auth & Learning)
- **Ephrahim Otieno** — Full Stack Developer (Community Features)
- **Craig Omore** — Full Stack Developer (Content & Admin)

---

## Demo Login Credentials

All demo accounts use the password: **`demo123`**

| Role | Username | Email | Password |
|------|----------|-------|----------|
| **Admin** | admin_user | admin@learnquest.com | demo123 |
| **Contributor** | demo_creator | creator@learnquest.com | demo123 |
| **Learner** | alex_learner | alex@example.com | demo123 |
| Contributor | jessica_wong | jessica@example.com | demo123 |
| Learner | david_kim | david@example.com | demo123 |
| Learner | sarah_jenkins | sarah@example.com | demo123 |

### Role Capabilities
- **Admin** — Full platform management: approve/reject learning paths, manage users (change roles, delete), view platform stats, plus all Contributor/Learner features.
- **Contributor** — Create and publish learning paths via Creator Studio, add modules and resources. Also has all Learner features.
- **Learner** — Browse and enroll in learning paths, complete resources and quizzes, earn XP/badges, view leaderboard, track progress.

---

## Quick Start

### Prerequisites
- Python 3.8+ (or Python 3.14 with UV)
- pipenv or UV (Python package manager)

### Installation

```bash
# Clone and enter the project
git clone git@github.com:MrNawir/LearnQuest-Backend.git
cd LearnQuest-Backend

# Install dependencies
pipenv install

# Create .env file
cp .env.example .env

# Activate virtual environment
pipenv shell

# Seed the database with demo data
python seed_data.py

# Run the server
python run.py
```

The API will be available at `http://localhost:5000`

### Reseed Database (reset to fresh state)

```bash
rm -f instance/learnquest.db
python seed_data.py
```

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login user |
| GET | `/api/auth/me` | Get current user (requires auth) |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/` | Get all users |
| GET | `/api/users/<id>` | Get user by ID |
| PUT | `/api/users/profile` | Update profile (requires auth) |
| GET | `/api/users/<id>/stats` | Get user stats |

### Learning Paths
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/learning-paths/` | Get all published paths |
| GET | `/api/learning-paths/<id>` | Get path with modules |
| POST | `/api/learning-paths/` | Create path (contributor/admin) |
| POST | `/api/learning-paths/<id>/modules` | Add module to path |
| POST | `/api/learning-paths/modules/<id>/resources` | Add resource to module |
| POST | `/api/learning-paths/<id>/rate` | Rate a path (1-5) |

### Progress & Enrollment
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/progress/enroll/<path_id>` | Enroll in a learning path |
| GET | `/api/progress/my-paths` | Get enrolled paths |
| GET | `/api/progress/path/<path_id>` | Get progress for a path |
| POST | `/api/progress/complete-resource/<id>` | Mark resource complete (+XP) |
| POST | `/api/progress/complete-module/<id>` | Mark module complete (+XP) |

### Quizzes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/quizzes/module/<module_id>/quiz` | Get quiz for a module |
| GET | `/api/quizzes/<id>` | Get quiz by ID |
| POST | `/api/quizzes/<id>/submit` | Submit quiz answers |
| GET | `/api/quizzes/<id>/attempts` | Get user's quiz attempts |

### Gamification
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/gamification/badges` | Get all badges |
| GET | `/api/gamification/badges/<user_id>` | Get user's earned badges |
| GET | `/api/gamification/leaderboard?period=weekly&limit=50` | Get leaderboard |
| GET | `/api/gamification/leaderboard/me` | Get current user's rank |
| GET | `/api/gamification/challenges` | Get active challenges |
| GET | `/api/gamification/achievements` | Get all achievements |
| POST | `/api/gamification/xp/add` | Add XP to current user |
| POST | `/api/gamification/streak/update` | Update learning streak |
| GET | `/api/gamification/streak/status` | Get streak status |

### Comments & Discussions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/comments?learning_path_id=X` | Get comments (paginated) |
| POST | `/api/comments` | Post a comment (+5 XP) |
| PUT | `/api/comments/<id>` | Edit comment (15-min window) |
| DELETE | `/api/comments/<id>` | Soft-delete comment |

### Admin (requires admin role)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/stats` | Platform-wide statistics |
| GET | `/api/admin/pending` | Pending learning path approvals |
| POST | `/api/admin/approve/<path_id>` | Approve a learning path |
| POST | `/api/admin/reject/<path_id>` | Reject a learning path |
| GET | `/api/admin/users?role=learner&search=` | List/search users |
| PUT | `/api/admin/users/<id>/role` | Change user role |
| DELETE | `/api/admin/users/<id>` | Delete a user |

### Resources
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/resources/` | Get all resources |
| GET | `/api/resources/<id>` | Get resource by ID |
| POST | `/api/resources/<id>/rate` | Rate a resource (1-5) |

---

## Tech Stack
- **Flask** — Python web framework
- **Flask-SQLAlchemy** — Database ORM
- **Flask-Migrate** — Database migrations
- **Flask-JWT-Extended** — JWT authentication
- **Flask-CORS** — Cross-Origin Resource Sharing
- **SQLite** (dev) / **PostgreSQL** (production)

## Project Structure
```
backend/
├── app/
│   ├── __init__.py          # App factory, blueprint registration
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py          # User model with roles
│   │   ├── learning_path.py # LearningPath, Module, Resource
│   │   ├── gamification.py  # Badge, Achievement, Challenge
│   │   ├── quiz.py          # Quiz, Question, QuizAttempt
│   │   ├── progress.py      # UserProgress, ResourceCompletion
│   │   └── comment.py       # Comment with replies
│   ├── routes/              # API blueprints
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── users.py         # User management
│   │   ├── learning_paths.py # Learning path CRUD
│   │   ├── resources.py     # Resource endpoints
│   │   ├── gamification.py  # Badges, leaderboard, XP, streaks
│   │   ├── quizzes.py       # Quiz endpoints
│   │   ├── progress.py      # Enrollment & progress tracking
│   │   ├── comments.py      # Discussion/comment endpoints
│   │   └── admin.py         # Admin dashboard endpoints
│   ├── services/            # Business logic
│   │   ├── streak_service.py
│   │   └── leaderboard_service.py
│   └── utils/               # Decorators and helpers
├── seed_data.py             # Database seeding script
├── run.py                   # Application entry point
└── Pipfile                  # Dependencies
```

## License
MIT


https://github.com/brimiq/LearnQuest-Frontend/tree/main
