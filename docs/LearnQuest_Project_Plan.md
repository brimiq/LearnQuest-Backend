# LearnQuest - Crowdsourced Learning Platform with Gamification

## Group 7 Project Plan

**Project Leader:** Ibrahim Abdu

---

## Team Members & Work Division

### 1. Ibrahim Abdu (Group Leader)
**Role:** Project Coordination, Backend Architecture & Integration

**Responsibilities:**
- Overall project coordination and task management
- Backend API architecture and database design
- Integration between frontend and backend
- Code reviews and merge conflict resolution
- Deployment and DevOps setup

**Key Tasks:**
- Set up Flask backend structure ✅
- Design and implement database models
- Create API endpoints for core features
- Manage Git repositories and branching strategy
- Coordinate team communication and deadlines

---

### 2. Bradley Murimi
**Role:** Backend Developer

**Responsibilities:**
- Implement authentication and authorization (JWT)
- Build gamification system (XP, points, badges, achievements)
- Create leaderboard and challenge APIs
- Database migrations and seeding
- API testing and documentation

**Key Tasks:**
- Implement user registration and login endpoints
- Create badge and achievement system
- Build leaderboard functionality
- Implement weekly/monthly challenges
- Write API tests using pytest

---

### 3. Joyce Njogu
**Role:** Frontend Developer (Lead)

**Responsibilities:**
- Implement UI components based on Figma designs
- Build responsive layouts with React and TailwindCSS
- Create reusable component library
- Handle frontend state management
- Ensure accessibility and UX best practices

**Key Tasks:**
- Build Dashboard page with stats cards
- Create Sidebar navigation component
- Implement Learning Paths display
- Build Achievement and Badge display components
- Create responsive mobile layouts

---

### 4. Julius Mutinda
**Role:** Frontend Developer

**Responsibilities:**
- Implement user authentication UI (login, register, profile)
- Build learning path and module views
- Create quiz and resource components
- Handle API integration on frontend
- Form validation and error handling

**Key Tasks:**
- Build Login and Registration pages
- Create Learning Path detail view
- Implement Module and Resource viewers
- Build Quiz component with scoring
- Handle JWT token management on frontend

---

### 5. Ephrahim Otieno
**Role:** Full Stack Developer (Focus: Community Features)

**Responsibilities:**
- Build community interaction features
- Implement rating and commenting system
- Create discussion forums under learning paths
- Handle real-time notifications (if time permits)
- Integration testing

**Key Tasks:**
- Build comment and discussion components
- Implement rating system (frontend + backend)
- Create user profile pages
- Build notification system
- Write integration tests

---

### 6. Craig Omore
**Role:** Full Stack Developer (Focus: Content & Admin)

**Responsibilities:**
- Build Creator Studio for contributors
- Implement admin dashboard and moderation tools
- Create learning path and resource creation forms
- Handle file uploads and media management
- Documentation and user guides

**Key Tasks:**
- Build Creator Studio page
- Implement admin approval workflow
- Create learning path creation wizard
- Build resource upload functionality
- Write user documentation

---

## Project Architecture

### Tech Stack

**Frontend:**
- React with TypeScript
- Vite (build tool)
- TailwindCSS (styling)
- React Router (navigation)
- Axios (API calls)
- Zustand or Context API (state management)

**Backend:**
- Flask (Python web framework)
- Flask-SQLAlchemy (ORM)
- Flask-JWT-Extended (authentication)
- Flask-CORS (cross-origin requests)
- SQLite (development) / PostgreSQL (production)

**Tools:**
- Git & GitHub (version control)
- Figma (design)
- Antigravity IDE (AI-assisted development)
- Postman (API testing)

---

## Getting Started with Antigravity IDE (Ubuntu Installation)

Antigravity is Google's AI-powered IDE (launched November 2025 with Gemini 3 Pro) that provides autonomous coding agents to help you write code faster. Here's how to install it on **Ubuntu**:

### Step 1: Update System Packages

Open your terminal and run:

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install Required Dependencies

```bash
sudo apt install curl gpg -y
```

### Step 3: Import Google Antigravity GPG Key

```bash
curl -fsSL https://us-central1-apt.pkg.dev/doc/repo-signing-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/google-antigravity.gpg
```

### Step 4: Add Google Antigravity Repository

```bash
echo "Types: deb
URIs: https://us-central1-apt.pkg.dev/projects/antigravity-auto-updater-dev/
Suites: antigravity-debian
Components: main
Signed-By: /usr/share/keyrings/google-antigravity.gpg" | sudo tee /etc/apt/sources.list.d/google-antigravity.sources > /dev/null
```

### Step 5: Install Antigravity

```bash
sudo apt update
sudo apt install antigravity -y
```

### Step 6: Verify Installation

```bash
dpkg-query -W -f='${Package} ${Version}\n' antigravity
which antigravity
```

### Step 7: Launch Antigravity

**From Terminal:**
```bash
# Launch Antigravity
antigravity

# Or open directly to your project folder
antigravity /path/to/LearnQuest/backend
antigravity /path/to/LearnQuest/frontend
```

**From Applications Menu:**
1. Click on **Activities** (top left corner)
2. Select **Show Applications** (grid icon at bottom of dock)
3. Type "Antigravity" in the search bar
4. Click the icon to launch

### Using Antigravity AI Chat

Once Antigravity is open:
1. Press `Ctrl+Shift+P` to open the command palette
2. Type "AI Chat" and select it, OR press `Ctrl+L` for quick chat
3. Paste the prompts below to get the AI to do the work for you!

---

## Antigravity Prompts by Role (Copy-Paste Ready!)

**IMPORTANT:** These prompts are designed to make Antigravity **do the work for you**. Just copy-paste them into the AI chat!

---

### For Bradley (Backend - Auth & Gamification)

**PROMPT 1 - Streak System (Copy this entire block):**
```
I need you to implement a complete streak tracking system for the LearnQuest Flask backend. 

Create a new file `app/services/streak_service.py` with the following:

1. A function `update_user_streak(user_id)` that:
   - Gets the user's last_active timestamp from the database
   - Checks if they were active yesterday (within 24-48 hours ago)
   - If yes: increment streak_days by 1
   - If no: reset streak_days to 1
   - Update last_active to now
   - Return the new streak count

2. A function `award_streak_bonus(user_id, streak_days)` that:
   - Awards 50 bonus XP for 7-day streaks
   - Awards 200 bonus XP for 30-day streaks
   - Awards 500 bonus XP for 100-day streaks
   - Creates a badge award if they reach these milestones

3. Add a new route in `app/routes/gamification.py`:
   - POST `/api/gamification/streak/update` - calls update_user_streak and award_streak_bonus

Use the existing User model from `app/models/user.py`. Write clean, production-ready code with proper error handling.
```

**PROMPT 2 - Leaderboard System (Copy this entire block):**
```
Create a complete leaderboard system for LearnQuest Flask backend.

Create `app/services/leaderboard_service.py` with:

1. `get_leaderboard(period='all_time', limit=100)` function that:
   - Supports periods: 'daily', 'weekly', 'monthly', 'all_time'
   - For daily/weekly/monthly: filter users by activity within that period
   - Returns list of {rank, user_id, username, avatar_url, xp, points}
   - Orders by XP descending

2. `get_user_rank(user_id, period='all_time')` function that:
   - Returns the user's current rank and surrounding users (+/- 2 positions)

3. Update `app/routes/gamification.py` with:
   - GET `/api/gamification/leaderboard?period=weekly&limit=50`
   - GET `/api/gamification/leaderboard/me` - get current user's rank

Use SQLAlchemy queries on the User model. Include proper JSON responses.
```

**PROMPT 3 - Pytest Tests (Copy this entire block):**
```
Create comprehensive pytest tests for the LearnQuest authentication system.

Create `tests/test_auth.py` with:

1. Fixtures for:
   - test_client (Flask test client)
   - test_user (create a test user in DB)
   - auth_headers (JWT token headers)

2. Test cases:
   - test_register_success - valid registration returns 201 and user data
   - test_register_duplicate_email - returns 409 conflict
   - test_register_duplicate_username - returns 409 conflict
   - test_register_missing_fields - returns 400 bad request
   - test_login_success - valid credentials return 200 and token
   - test_login_wrong_password - returns 401 unauthorized
   - test_login_nonexistent_user - returns 401 unauthorized
   - test_get_current_user_authenticated - returns user data
   - test_get_current_user_no_token - returns 401

Use pytest fixtures, proper assertions, and clean up test data after each test. Create `tests/__init__.py` and `tests/conftest.py` as needed.
```

---

### For Joyce (Frontend - UI Components)

**PROMPT 1 - Connect Dashboard to Backend API (Copy this entire block):**
```
I need you to connect the existing LearnQuest React Dashboard component to the Flask backend API.

Modify `src/components/Dashboard.tsx` to:

1. Create an API service file `src/services/api.ts` with:
   - axios instance with baseURL 'http://localhost:5000/api'
   - Request interceptor to add JWT token from localStorage
   - Response interceptor for error handling

2. Create `src/services/userService.ts` with:
   - getCurrentUser() - GET /api/auth/me
   - getUserStats(userId) - GET /api/users/:id/stats
   - updateProfile(data) - PUT /api/users/profile

3. Create `src/services/learningPathService.ts` with:
   - getLearningPaths() - GET /api/learning-paths
   - getLearningPath(id) - GET /api/learning-paths/:id
   - getUserProgress(pathId) - GET /api/learning-paths/:id/progress

4. Update Dashboard.tsx to:
   - Fetch real user data on mount using useEffect
   - Display actual stats (xp, streak_days, hours_learned) from API
   - Show loading state while fetching
   - Handle errors gracefully with toast notifications

5. Create a Zustand store `src/stores/userStore.ts` for:
   - user state
   - isLoading state  
   - fetchUser action
   - updateUser action

Use TypeScript interfaces for all API responses. The backend is already running at localhost:5000.
```

**PROMPT 2 - Responsive Mobile Layout (Copy this entire block):**
```
Make the LearnQuest Dashboard and Layout components fully responsive for mobile devices.

Update `src/components/Layout.tsx` to:
1. Add a mobile hamburger menu button (visible on screens < 768px)
2. Create a slide-out drawer for the sidebar on mobile
3. Hide the desktop sidebar on mobile
4. Add smooth transition animations for the drawer

Update `src/components/Dashboard.tsx` to:
1. Stack stats cards vertically on mobile (1 column)
2. Show 2 columns on tablet (md breakpoint)
3. Show 4 columns on desktop (lg breakpoint)
4. Make the Daily Challenge card full-width on mobile
5. Adjust font sizes for mobile readability

Use TailwindCSS responsive prefixes (sm:, md:, lg:, xl:). Add touch-friendly tap targets (min 44px). Test at breakpoints: 320px, 768px, 1024px, 1440px.
```

---

### For Julius (Frontend - Auth & Learning)

**PROMPT 1 - Complete Auth System (Copy this entire block):**
```
Build a complete authentication system for the LearnQuest React frontend.

Create the following files:

1. `src/services/authService.ts`:
   - login(email, password) - POST /api/auth/login, store token in localStorage
   - register(username, email, password) - POST /api/auth/register
   - logout() - clear localStorage and redirect
   - getToken() - get token from localStorage
   - isAuthenticated() - check if valid token exists

2. `src/stores/authStore.ts` (Zustand):
   - user, token, isAuthenticated, isLoading states
   - login, register, logout, checkAuth actions

3. `src/components/auth/LoginForm.tsx`:
   - Email and password inputs with validation
   - "Remember me" checkbox
   - Submit button with loading state
   - Link to register page
   - Error display for invalid credentials
   - Use react-hook-form for form handling

4. `src/components/auth/RegisterForm.tsx`:
   - Username, email, password, confirm password inputs
   - Password strength indicator
   - Terms acceptance checkbox
   - Client-side validation (email format, password match, min 8 chars)
   - Link to login page

5. `src/components/auth/ProtectedRoute.tsx`:
   - Wrapper component that checks authentication
   - Redirects to /login if not authenticated
   - Shows loading spinner while checking

6. Update `src/App.tsx` to use react-router-dom with:
   - / - Landing page (public)
   - /login - Login page (public)
   - /register - Register page (public)  
   - /dashboard - Dashboard (protected)
   - /learning/* - Learning pages (protected)

Use TypeScript, handle all error states, add toast notifications for success/error.
```

**PROMPT 2 - Quiz Component (Copy this entire block):**
```
Build a complete Quiz component for LearnQuest that handles assessments within learning modules.

Create the following:

1. `src/types/quiz.ts`:
   - Question interface: {id, question, options: string[], correctAnswer: number, explanation: string}
   - QuizResult interface: {score, totalQuestions, xpEarned, passed, answers: UserAnswer[]}
   - UserAnswer interface: {questionId, selectedAnswer, isCorrect}

2. `src/components/quiz/Quiz.tsx`:
   - Props: questions: Question[], onComplete: (result: QuizResult) => void, passingScore: number
   - State: currentQuestion, answers, timeRemaining (optional timer)
   - Features:
     * Show one question at a time with progress indicator (1/10)
     * Multiple choice with radio buttons
     * "Next" and "Previous" navigation buttons
     * Review mode before submission
     * Animated transitions between questions

3. `src/components/quiz/QuizResult.tsx`:
   - Display score as percentage with circular progress
   - Show pass/fail status with appropriate colors
   - Display XP earned (10 XP per correct answer, bonus for perfect score)
   - "Review Answers" button to see correct/incorrect
   - "Continue" button to proceed to next module

4. `src/services/quizService.ts`:
   - getQuiz(moduleId) - GET /api/modules/:id/quiz
   - submitQuiz(moduleId, answers) - POST /api/modules/:id/quiz/submit
   - Response includes XP awarded and updates user progress

Use Framer Motion for animations, TailwindCSS for styling. Make it mobile-friendly.
```

---

### For Ephrahim (Full Stack - Community)

**PROMPT 1 - Complete Comment System Backend (Copy this entire block):**
```
Build a complete commenting system for the LearnQuest Flask backend.

Create `app/models/comment.py`:
```python
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'))
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))  # For replies
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)  # Soft delete
    
    user = db.relationship('User', backref='comments')
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]))
```

Create `app/routes/comments.py` with:
- GET /api/comments?learning_path_id=X or resource_id=X - list comments with replies
- POST /api/comments - create comment (requires auth)
- PUT /api/comments/:id - edit own comment (requires auth)
- DELETE /api/comments/:id - soft delete own comment (requires auth)

Include:
- Pagination (20 per page)
- Nested replies (1 level deep)
- User info (username, avatar) in responses
- Only allow editing within 15 minutes
- XP award: +5 XP for posting a comment

Register the blueprint in app/__init__.py. Write clean code with proper error handling.
```

**PROMPT 2 - Comment System Frontend (Copy this entire block):**
```
Build the frontend Comment components for LearnQuest React.

Create:

1. `src/services/commentService.ts`:
   - getComments(learningPathId?, resourceId?, page?) - GET /api/comments
   - createComment(content, learningPathId?, resourceId?, parentId?) - POST
   - updateComment(id, content) - PUT
   - deleteComment(id) - DELETE

2. `src/components/comments/CommentSection.tsx`:
   - Props: learningPathId or resourceId
   - Fetches and displays comments with infinite scroll
   - "Add comment" form at top (textarea + submit button)
   - Shows login prompt if not authenticated

3. `src/components/comments/CommentCard.tsx`:
   - Displays: avatar, username, timestamp ("2 hours ago"), content
   - "Reply" button that shows reply form
   - "Edit" and "Delete" buttons (only for own comments)
   - Nested replies indented underneath
   - Edit mode with save/cancel buttons
   - Delete confirmation dialog

4. `src/components/comments/CommentForm.tsx`:
   - Reusable form for new comments and replies
   - Textarea with placeholder
   - Character count (max 1000)
   - Submit button with loading state
   - Cancel button (for replies/edits)

Use optimistic updates for better UX. Show toast on success/error. Style with TailwindCSS.
```

---

### For Craig (Full Stack - Admin & Creator)

**PROMPT 1 - Learning Path Creation Wizard (Copy this entire block):**
```
Build a complete Learning Path creation wizard for the LearnQuest Creator Studio.

Create `src/components/creator/LearningPathWizard.tsx` with 4 steps:

**Step 1 - Basic Info:**
- Title input (required, max 100 chars)
- Description textarea (required, max 500 chars)
- Category dropdown (Programming, Design, Data Science, DevOps, etc.)
- Difficulty radio buttons (Beginner, Intermediate, Advanced)
- Cover image upload with preview
- Estimated duration input

**Step 2 - Modules:**
- "Add Module" button
- Draggable list of modules (react-beautiful-dnd or similar)
- Each module has: title, description, order number
- Delete module button with confirmation
- Minimum 1 module required

**Step 3 - Resources:**
- Select a module from dropdown
- "Add Resource" button for selected module
- Resource types: Video (URL), Article (URL), Document (upload), Quiz
- Each resource: title, type, URL/content, duration estimate
- Reorder resources within module

**Step 4 - Review & Submit:**
- Summary of learning path
- List all modules and resources
- Total estimated duration
- "Save as Draft" and "Submit for Review" buttons

Create `src/services/creatorService.ts`:
- createLearningPath(data) - POST /api/learning-paths
- addModule(pathId, data) - POST /api/learning-paths/:id/modules  
- addResource(moduleId, data) - POST /api/modules/:id/resources
- submitForReview(pathId) - POST /api/learning-paths/:id/submit

Use react-hook-form with Zod validation. Show progress bar at top. Save draft to localStorage.
```

**PROMPT 2 - Admin Dashboard (Copy this entire block):**
```
Build a complete Admin Dashboard for LearnQuest.

Create `src/components/admin/AdminDashboard.tsx` with:

**Stats Overview Row:**
- Total Users card (with growth % from last week)
- Total Learning Paths card
- Active Learners Today card
- Pending Approvals card (with alert badge)

**Pending Approvals Section:**
- Table with: Title, Creator, Category, Submitted Date, Actions
- Actions: "Review", "Approve", "Reject"
- Click "Review" opens modal with full path preview
- "Approve" adds to published paths, notifies creator, awards XP
- "Reject" opens modal for rejection reason, notifies creator

**User Management Section:**
- Searchable table with: Username, Email, Role, XP, Status, Joined
- Filter by role (Admin, Contributor, Learner)
- Actions: Change role, Suspend, Delete
- Confirmation dialogs for destructive actions

**Content Moderation Queue:**
- Reported comments/resources
- Reporter info, reason, content preview
- Actions: Dismiss, Warn User, Remove Content, Ban User

Create backend routes in `app/routes/admin.py`:
- GET /api/admin/stats - dashboard statistics
- GET /api/admin/pending - pending learning paths
- POST /api/admin/approve/:id - approve path
- POST /api/admin/reject/:id - reject with reason
- GET /api/admin/users - user list with filters
- PUT /api/admin/users/:id/role - change user role

Add admin role check middleware. Only users with role='admin' can access.
```

---

## Git Workflow

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch
- `feature/<name>` - Feature branches
- `<username>/dev` - Personal development branches

### Creating Your Branch

```bash
# Clone the backend repo
git clone git@github.com:MrNawir/LearnQuest-Backend.git
cd LearnQuest-Backend

# Create your personal dev branch
git checkout -b <your-name>/dev

# Example:
git checkout -b bradley/dev
git checkout -b joyce/dev
git checkout -b julius/dev
git checkout -b ephrahim/dev
git checkout -b craig/dev
```

### Daily Workflow

```bash
# Start of day - get latest changes
git checkout main
git pull origin main
git checkout <your-name>/dev
git merge main

# Work on your features...

# End of day - push your changes
git add .
git commit -m "Descriptive message about what you did"
git push origin <your-name>/dev
```

### Creating Pull Requests

1. Push your branch to GitHub
2. Go to the repository on GitHub
3. Click "Compare & pull request"
4. Add a description of your changes
5. Request review from Ibrahim (group leader)
6. Address any feedback
7. Once approved, it will be merged to main

---

## Project Timeline

### Week 1: Setup & Core Features
- [x] Set up Flask backend structure
- [x] Initialize Git repositories
- [ ] Set up frontend project structure
- [ ] Implement user authentication (frontend + backend)
- [ ] Create database models

### Week 2: Learning Paths & Gamification
- [ ] Build learning path CRUD operations
- [ ] Implement module and resource management
- [ ] Create gamification system (XP, badges)
- [ ] Build dashboard UI

### Week 3: Community & Creator Features
- [ ] Implement rating and commenting
- [ ] Build Creator Studio
- [ ] Create leaderboard
- [ ] Implement challenges

### Week 4: Polish & Testing
- [ ] Integration testing
- [ ] Bug fixes
- [ ] UI/UX polish
- [ ] Documentation
- [ ] Final presentation preparation

---

## API Reference

### Base URL
- Development: `http://localhost:5000/api`

### Authentication Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login user |
| GET | `/auth/me` | Get current user |

### User Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/` | Get all users |
| GET | `/users/:id` | Get user by ID |
| PUT | `/users/profile` | Update profile |
| GET | `/users/:id/stats` | Get user stats |

### Learning Path Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/learning-paths/` | Get all paths |
| GET | `/learning-paths/:id` | Get path by ID |
| POST | `/learning-paths/` | Create path |
| POST | `/learning-paths/:id/modules` | Add module |
| POST | `/learning-paths/:id/rate` | Rate path |

### Gamification Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/gamification/badges` | Get all badges |
| GET | `/gamification/badges/:userId` | Get user badges |
| GET | `/gamification/leaderboard` | Get leaderboard |
| GET | `/gamification/challenges` | Get challenges |
| GET | `/gamification/achievements` | Get achievements |

---

## Figma Design Reference

Our designs are available at:
**[LearnQuest Figma Design](https://www.figma.com/design/EzvyETFHq479ulBnTppx02/LearnQuest)**

### Key Screens
1. **Dashboard** - Main user dashboard with stats and learning paths
2. **Login/Register** - Authentication screens
3. **Learning Path View** - Detailed path with modules
4. **Creator Studio** - Content creation interface
5. **Achievements** - Badges and achievements display
6. **Leaderboard** - Global rankings

---

## Contact & Communication

- **Group Leader:** Ibrahim Abdu
- **GitHub Org:** [LearnQuest Backend](https://github.com/MrNawir/LearnQuest-Backend)
- **Figma:** [LearnQuest Design](https://www.figma.com/design/EzvyETFHq479ulBnTppx02/LearnQuest)

---

*Let's build something amazing together! 🚀*
