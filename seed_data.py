"""
Seed data for LearnQuest database with PostgreSQL.
Run with: python seed_data.py
"""
from app import create_app, db
from app.models import (
    User, Badge, Achievement, Challenge,
    LearningPath, Module, Resource,
    Quiz, Question, Report, Notification
)
from datetime import datetime, timedelta
import json


def seed_badges():
    badges = [
        {'name': 'First Steps', 'description': 'Complete your first lesson', 'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=rocket&backgroundColor=3b82f6', 'badge_type': 'bronze', 'is_seasonal': False},
        {'name': 'Week Warrior', 'description': 'Maintain a 7-day learning streak', 'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=fire&backgroundColor=ff6b35', 'badge_type': 'silver', 'is_seasonal': False},
        {'name': 'Quiz Master', 'description': 'Score 100% on 5 quizzes', 'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=brain&backgroundColor=9333ea', 'badge_type': 'gold', 'is_seasonal': False},
        {'name': 'Social Butterfly', 'description': 'Post 10 helpful comments', 'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=chat&backgroundColor=06b6d4', 'badge_type': 'bronze', 'is_seasonal': False},
        {'name': 'Code Ninja', 'description': 'Complete 50 coding challenges', 'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=code&backgroundColor=22c55e', 'badge_type': 'platinum', 'is_seasonal': False},
        {'name': 'Mentor', 'description': 'Help 10 other learners', 'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=heart&backgroundColor=ec4899', 'badge_type': 'gold', 'is_seasonal': False},
        {'name': 'Path Finder', 'description': 'Complete your first learning path', 'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=map&backgroundColor=10b981', 'badge_type': 'silver', 'is_seasonal': False},
        {'name': 'Early Bird', 'description': 'Complete a lesson before 8 AM', 'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=sun&backgroundColor=ffd700', 'badge_type': 'bronze', 'is_seasonal': False},
        {'name': 'Streak Legend', 'description': 'Maintain a 30-day learning streak', 'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=flame&backgroundColor=ef4444', 'badge_type': 'platinum', 'is_seasonal': False},
        {'name': 'Data Science Month', 'description': 'Complete 3 data science paths in March', 'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=chart&backgroundColor=f59e0b', 'badge_type': 'special', 'is_seasonal': True},
    ]
    for b in badges:
        if not Badge.query.filter_by(name=b['name']).first():
            db.session.add(Badge(**b))
    db.session.commit()
    print(f"Created {len(badges)} badges")


def seed_achievements():
    achievements = [
        {'name': 'Getting Started', 'description': 'Complete your first module', 'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=star&backgroundColor=ffd700', 'xp_reward': 50, 'points_reward': 25, 'requirement_type': 'modules_completed', 'requirement_value': 1},
        {'name': 'Dedicated Learner', 'description': 'Complete 10 modules', 'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=trophy&backgroundColor=f59e0b', 'xp_reward': 200, 'points_reward': 100, 'requirement_type': 'modules_completed', 'requirement_value': 10},
        {'name': 'Path Master', 'description': 'Complete 3 learning paths', 'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=crown&backgroundColor=9333ea', 'xp_reward': 500, 'points_reward': 250, 'requirement_type': 'paths_completed', 'requirement_value': 3},
        {'name': 'On Fire', 'description': 'Maintain a 14-day streak', 'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=fire&backgroundColor=ef4444', 'xp_reward': 150, 'points_reward': 75, 'requirement_type': 'streak', 'requirement_value': 14},
        {'name': 'Knowledge Seeker', 'description': 'Complete 50 resources', 'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=gem&backgroundColor=06b6d4', 'xp_reward': 300, 'points_reward': 150, 'requirement_type': 'resources_completed', 'requirement_value': 50},
    ]
    for a in achievements:
        if not Achievement.query.filter_by(name=a['name']).first():
            db.session.add(Achievement(**a))
    db.session.commit()
    print(f"Created {len(achievements)} achievements")


def seed_challenges():
    now = datetime.utcnow()
    challenges = [
        {'title': 'Weekly Sprint: Complete 5 Lessons', 'description': 'Complete any 5 lessons this week to earn bonus XP and a special badge!', 'challenge_type': 'weekly', 'xp_reward': 100, 'points_reward': 50, 'requirement_type': 'lessons_completed', 'requirement_value': 5, 'start_date': now, 'end_date': now + timedelta(days=7), 'is_active': True},
        {'title': 'Monthly Master: Finish 2 Learning Paths', 'description': 'Complete 2 full learning paths this month. Show your dedication!', 'challenge_type': 'monthly', 'xp_reward': 500, 'points_reward': 250, 'requirement_type': 'paths_completed', 'requirement_value': 2, 'start_date': now, 'end_date': now + timedelta(days=30), 'is_active': True},
        {'title': 'Quiz Champion: Score 90%+ on 3 Quizzes', 'description': 'Ace 3 quizzes with a score of 90% or higher this week.', 'challenge_type': 'weekly', 'xp_reward': 150, 'points_reward': 75, 'requirement_type': 'quiz_score', 'requirement_value': 3, 'start_date': now, 'end_date': now + timedelta(days=7), 'is_active': True},
        {'title': 'Spring Learning Festival', 'description': 'Participate in the Spring Learning Festival! Complete any 10 resources to earn the exclusive Spring badge.', 'challenge_type': 'seasonal', 'xp_reward': 300, 'points_reward': 150, 'requirement_type': 'resources_completed', 'requirement_value': 10, 'start_date': now, 'end_date': now + timedelta(days=60), 'is_active': True},
    ]
    for c in challenges:
        if not Challenge.query.filter_by(title=c['title']).first():
            db.session.add(Challenge(**c))
    db.session.commit()
    print(f"Created {len(challenges)} challenges")


def seed_users():
    users_data = [
        {'username': 'admin', 'email': 'admin@learnquest.com', 'password': 'demo123', 'role': 'admin', 'xp': 5000, 'points': 2500, 'streak_days': 30, 'hours_learned': 120, 'bio': 'Platform administrator', 'avatar_url': 'https://api.dicebear.com/7.x/avataaars/svg?seed=admin'},
        {'username': 'creator', 'email': 'creator@learnquest.com', 'password': 'demo123', 'role': 'contributor', 'xp': 3500, 'points': 1750, 'streak_days': 14, 'hours_learned': 80, 'bio': 'Full-stack developer & content creator', 'avatar_url': 'https://api.dicebear.com/7.x/avataaars/svg?seed=creator'},
        {'username': 'alex_learner', 'email': 'alex@example.com', 'password': 'demo123', 'role': 'learner', 'xp': 1200, 'points': 600, 'streak_days': 7, 'hours_learned': 25, 'bio': 'Learning web development!', 'avatar_url': 'https://api.dicebear.com/7.x/avataaars/svg?seed=alex'},
        {'username': 'sarah_dev', 'email': 'sarah@example.com', 'password': 'demo123', 'role': 'learner', 'xp': 2800, 'points': 1400, 'streak_days': 21, 'hours_learned': 55, 'bio': 'Aspiring data scientist', 'avatar_url': 'https://api.dicebear.com/7.x/avataaars/svg?seed=sarah'},
        {'username': 'mike_coder', 'email': 'mike@example.com', 'password': 'demo123', 'role': 'contributor', 'xp': 4200, 'points': 2100, 'streak_days': 45, 'hours_learned': 95, 'bio': 'Backend engineer, Python enthusiast', 'avatar_url': 'https://api.dicebear.com/7.x/avataaars/svg?seed=mike'},
    ]
    for u in users_data:
        if not User.query.filter_by(email=u['email']).first():
            user = User(
                username=u['username'], email=u['email'], role=u['role'],
                xp=u['xp'], points=u['points'], streak_days=u['streak_days'],
                hours_learned=u['hours_learned'], bio=u['bio'], avatar_url=u['avatar_url']
            )
            user.set_password(u['password'])
            db.session.add(user)
    db.session.commit()
    print(f"Created {len(users_data)} demo users")


def seed_learning_paths():
    creator = User.query.filter_by(email='creator@learnquest.com').first()
    mike = User.query.filter_by(email='mike@example.com').first()
    if not creator:
        return

    paths_data = [
        {
            'title': 'Full-Stack Web Development',
            'description': 'Master HTML, CSS, JavaScript, React, and Node.js to become a complete web developer. This comprehensive path takes you from zero to building production-ready web applications.',
            'category': 'Web Development',
            'difficulty': 'beginner',
            'image_url': 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800&h=400&fit=crop',
            'xp_reward': 500,
            'creator_id': creator.id,
            'is_published': True,
            'is_approved': True,
            'rating': 4.7,
            'total_ratings': 128,
            'enrolled_count': 342,
            'modules': [
                {
                    'title': 'HTML & CSS Fundamentals',
                    'description': 'Learn the building blocks of the web',
                    'order': 1,
                    'xp_reward': 75,
                    'resources': [
                        {'title': 'HTML Crash Course For Absolute Beginners', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=UB1O30fR-EE', 'description': 'Complete HTML tutorial for beginners by Traversy Media'},
                        {'title': 'CSS Crash Course For Absolute Beginners', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=yfoY53QXEnI', 'description': 'Learn CSS from scratch with Traversy Media'},
                        {'title': 'Flexbox in 15 Minutes', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=fYq5PXgSsbE', 'description': 'Quick and clear flexbox tutorial by Web Dev Simplified'},
                        {'title': 'MDN CSS Box Model', 'type': 'article', 'url': 'https://developer.mozilla.org/en-US/docs/Learn/CSS/Building_blocks/The_box_model', 'description': 'Official Mozilla documentation on the CSS Box Model'},
                    ],
                    'quiz': {
                        'title': 'HTML & CSS Basics Quiz',
                        'description': 'Test your knowledge of HTML and CSS fundamentals',
                        'passing_score': 70,
                        'xp_reward': 50,
                        'questions': [
                            {'text': 'What does HTML stand for?', 'type': 'multiple_choice', 'options': ['Hyper Text Markup Language', 'High Tech Modern Language', 'Hyper Transfer Markup Language', 'Home Tool Markup Language'], 'correct': 0, 'explanation': 'HTML stands for Hyper Text Markup Language, the standard markup language for web pages.', 'points': 10},
                            {'text': 'Which CSS property is used to change the text color?', 'type': 'multiple_choice', 'options': ['font-color', 'text-color', 'color', 'foreground-color'], 'correct': 2, 'explanation': 'The "color" property is used to set the text color in CSS.', 'points': 10},
                            {'text': 'Which HTML tag is used for the largest heading?', 'type': 'multiple_choice', 'options': ['<heading>', '<h6>', '<h1>', '<head>'], 'correct': 2, 'explanation': '<h1> defines the largest heading. Headings go from <h1> (largest) to <h6> (smallest).', 'points': 10},
                            {'text': 'CSS Flexbox is a one-dimensional layout method.', 'type': 'true_false', 'options': ['True', 'False'], 'correct': 0, 'explanation': 'Flexbox is indeed a one-dimensional layout method for arranging items in rows or columns.', 'points': 10},
                            {'text': 'Which CSS property controls the space between elements?', 'type': 'multiple_choice', 'options': ['spacing', 'margin', 'padding', 'Both margin and padding'], 'correct': 3, 'explanation': 'Both margin (outside space) and padding (inside space) control spacing.', 'points': 10},
                        ]
                    }
                },
                {
                    'title': 'JavaScript Essentials',
                    'description': 'Master JavaScript fundamentals and modern ES6+ features',
                    'order': 2,
                    'xp_reward': 100,
                    'resources': [
                        {'title': 'JavaScript Crash Course For Beginners', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=hdI2bqOjy3c', 'description': 'Complete JS tutorial by Traversy Media'},
                        {'title': 'JavaScript ES6 Tutorial', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=NCwa_xi0Uuc', 'description': 'ES6 features explained by Programming with Mosh'},
                        {'title': 'Async JavaScript - Callbacks, Promises, Async/Await', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=PoRJizFvM7s', 'description': 'Master asynchronous JavaScript patterns'},
                        {'title': 'JavaScript.info - Modern Tutorial', 'type': 'article', 'url': 'https://javascript.info/', 'description': 'Comprehensive modern JavaScript tutorial'},
                    ],
                    'quiz': {
                        'title': 'JavaScript Fundamentals Quiz',
                        'description': 'Test your JavaScript knowledge',
                        'passing_score': 70,
                        'xp_reward': 50,
                        'questions': [
                            {'text': 'Which keyword declares a block-scoped variable?', 'type': 'multiple_choice', 'options': ['var', 'let', 'const', 'Both let and const'], 'correct': 3, 'explanation': 'Both let and const are block-scoped. var is function-scoped.', 'points': 10},
                            {'text': 'What does "===" check in JavaScript?', 'type': 'multiple_choice', 'options': ['Value only', 'Type only', 'Value and type', 'Reference'], 'correct': 2, 'explanation': '=== is the strict equality operator that checks both value and type.', 'points': 10},
                            {'text': 'Arrow functions have their own "this" context.', 'type': 'true_false', 'options': ['True', 'False'], 'correct': 1, 'explanation': 'Arrow functions do NOT have their own this. They inherit it from the enclosing scope.', 'points': 10},
                            {'text': 'What is the output of typeof null?', 'type': 'multiple_choice', 'options': ['"null"', '"undefined"', '"object"', '"boolean"'], 'correct': 2, 'explanation': 'typeof null returns "object" - this is a well-known JavaScript quirk.', 'points': 10},
                            {'text': 'Which method converts JSON string to JavaScript object?', 'type': 'multiple_choice', 'options': ['JSON.stringify()', 'JSON.parse()', 'JSON.convert()', 'JSON.toObject()'], 'correct': 1, 'explanation': 'JSON.parse() converts a JSON string into a JavaScript object.', 'points': 10},
                        ]
                    }
                },
                {
                    'title': 'React.js Framework',
                    'description': 'Build modern UIs with React components and hooks',
                    'order': 3,
                    'xp_reward': 100,
                    'resources': [
                        {'title': 'React JS Full Course for Beginners', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=RVFAyFWO4go', 'description': 'Complete React course by Dave Gray'},
                        {'title': 'React Hooks Tutorial', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=TNhaISOUy6Q', 'description': 'All React hooks explained by Fireship'},
                        {'title': 'React Official Tutorial', 'type': 'article', 'url': 'https://react.dev/learn', 'description': 'Official React documentation and tutorial'},
                    ],
                    'quiz': {
                        'title': 'React Fundamentals Quiz',
                        'description': 'Test your React knowledge',
                        'passing_score': 70,
                        'xp_reward': 50,
                        'questions': [
                            {'text': 'What hook is used for side effects in React?', 'type': 'multiple_choice', 'options': ['useState', 'useEffect', 'useContext', 'useReducer'], 'correct': 1, 'explanation': 'useEffect is the hook for performing side effects like data fetching, subscriptions, etc.', 'points': 10},
                            {'text': 'JSX stands for JavaScript XML.', 'type': 'true_false', 'options': ['True', 'False'], 'correct': 0, 'explanation': 'JSX stands for JavaScript XML. It allows writing HTML-like syntax in JavaScript.', 'points': 10},
                            {'text': 'What is the virtual DOM?', 'type': 'multiple_choice', 'options': ['A copy of the real DOM in memory', 'A browser API', 'A CSS framework', 'A JavaScript engine'], 'correct': 0, 'explanation': 'The virtual DOM is a lightweight copy of the real DOM kept in memory for efficient updates.', 'points': 10},
                        ]
                    }
                },
            ]
        },
        {
            'title': 'Python for Data Science',
            'description': 'Learn Python programming and essential data science libraries including NumPy, Pandas, and Matplotlib. Perfect for aspiring data analysts and scientists.',
            'category': 'Data Science',
            'difficulty': 'intermediate',
            'image_url': 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=800&h=400&fit=crop',
            'xp_reward': 600,
            'creator_id': mike.id if mike else creator.id,
            'is_published': True,
            'is_approved': True,
            'rating': 4.8,
            'total_ratings': 95,
            'enrolled_count': 256,
            'modules': [
                {
                    'title': 'Python Fundamentals',
                    'description': 'Core Python programming concepts',
                    'order': 1,
                    'xp_reward': 75,
                    'resources': [
                        {'title': 'Python Tutorial - Full Course for Beginners', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=_uQrJ0TkZlc', 'description': 'Complete Python tutorial by Programming with Mosh'},
                        {'title': 'Python Official Tutorial', 'type': 'article', 'url': 'https://docs.python.org/3/tutorial/', 'description': 'Official Python documentation tutorial'},
                        {'title': 'Python Functions and Modules', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=9Os0o3wzS_I', 'description': 'Functions, modules, and packages in Python'},
                    ],
                    'quiz': {
                        'title': 'Python Basics Quiz',
                        'description': 'Test your Python fundamentals',
                        'passing_score': 70,
                        'xp_reward': 50,
                        'questions': [
                            {'text': 'Which keyword is used to define a function in Python?', 'type': 'multiple_choice', 'options': ['function', 'func', 'def', 'define'], 'correct': 2, 'explanation': 'The "def" keyword is used to define functions in Python.', 'points': 10},
                            {'text': 'Python is a statically typed language.', 'type': 'true_false', 'options': ['True', 'False'], 'correct': 1, 'explanation': 'Python is dynamically typed - variable types are determined at runtime.', 'points': 10},
                            {'text': 'What does len() do in Python?', 'type': 'multiple_choice', 'options': ['Returns the type', 'Returns the length', 'Returns the last element', 'Returns a range'], 'correct': 1, 'explanation': 'len() returns the number of items in an object (string length, list size, etc).', 'points': 10},
                        ]
                    }
                },
                {
                    'title': 'Data Analysis with Pandas',
                    'description': 'Master data manipulation and analysis',
                    'order': 2,
                    'xp_reward': 100,
                    'resources': [
                        {'title': 'Pandas Tutorial for Beginners', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=vmEHCJofslg', 'description': 'Complete Pandas tutorial by Kevin Markham'},
                        {'title': 'NumPy Tutorial for Beginners', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=QUT1VHiLmmI', 'description': 'NumPy fundamentals for data science'},
                        {'title': 'Pandas Documentation', 'type': 'article', 'url': 'https://pandas.pydata.org/docs/getting_started/intro_tutorials/', 'description': 'Official Pandas getting started tutorials'},
                    ],
                    'quiz': {
                        'title': 'Data Analysis Quiz',
                        'description': 'Test your Pandas and data analysis skills',
                        'passing_score': 70,
                        'xp_reward': 50,
                        'questions': [
                            {'text': 'What is the primary data structure in Pandas?', 'type': 'multiple_choice', 'options': ['Array', 'DataFrame', 'Dictionary', 'Matrix'], 'correct': 1, 'explanation': 'DataFrame is the primary data structure in Pandas for tabular data.', 'points': 10},
                            {'text': 'Which method reads a CSV file into a DataFrame?', 'type': 'multiple_choice', 'options': ['pd.load_csv()', 'pd.read_csv()', 'pd.import_csv()', 'pd.open_csv()'], 'correct': 1, 'explanation': 'pd.read_csv() is the standard method to read CSV files into DataFrames.', 'points': 10},
                        ]
                    }
                },
            ]
        },
        {
            'title': 'DevOps & Cloud Computing',
            'description': 'Learn Docker, Kubernetes, CI/CD pipelines, and cloud deployment. Essential skills for modern software engineering teams.',
            'category': 'DevOps',
            'difficulty': 'advanced',
            'image_url': 'https://images.unsplash.com/photo-1667372393119-3d4c48d07fc9?w=800&h=400&fit=crop',
            'xp_reward': 700,
            'creator_id': creator.id,
            'is_published': True,
            'is_approved': True,
            'rating': 4.5,
            'total_ratings': 67,
            'enrolled_count': 178,
            'modules': [
                {
                    'title': 'Docker Fundamentals',
                    'description': 'Containerize applications with Docker',
                    'order': 1,
                    'xp_reward': 100,
                    'resources': [
                        {'title': 'Docker Tutorial for Beginners', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=fqMOX6JJhGo', 'description': 'Full Docker course by TechWorld with Nana'},
                        {'title': 'Docker in 100 Seconds', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=Gjnup-PuquQ', 'description': 'Quick Docker overview by Fireship'},
                        {'title': 'Docker Official Getting Started', 'type': 'article', 'url': 'https://docs.docker.com/get-started/', 'description': 'Official Docker getting started guide'},
                    ],
                    'quiz': {
                        'title': 'Docker Basics Quiz',
                        'description': 'Test your Docker knowledge',
                        'passing_score': 70,
                        'xp_reward': 50,
                        'questions': [
                            {'text': 'What file defines a Docker image?', 'type': 'multiple_choice', 'options': ['docker-compose.yml', 'Dockerfile', 'package.json', '.dockerignore'], 'correct': 1, 'explanation': 'A Dockerfile contains instructions to build a Docker image.', 'points': 10},
                            {'text': 'Docker containers share the host OS kernel.', 'type': 'true_false', 'options': ['True', 'False'], 'correct': 0, 'explanation': 'Unlike VMs, Docker containers share the host OS kernel, making them lightweight.', 'points': 10},
                        ]
                    }
                },
                {
                    'title': 'CI/CD Pipelines',
                    'description': 'Automate testing and deployment',
                    'order': 2,
                    'xp_reward': 100,
                    'resources': [
                        {'title': 'GitHub Actions Tutorial', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=R8_veQiYBjI', 'description': 'Complete GitHub Actions CI/CD tutorial by TechWorld with Nana'},
                        {'title': 'CI/CD Explained', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=scEDHsr3APg', 'description': 'CI/CD concepts explained by Fireship'},
                    ],
                    'quiz': None
                },
            ]
        },
        {
            'title': 'Mobile App Development with React Native',
            'description': 'Build cross-platform mobile apps using React Native and Expo. Create iOS and Android apps with a single codebase.',
            'category': 'Mobile Development',
            'difficulty': 'intermediate',
            'image_url': 'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=800&h=400&fit=crop',
            'xp_reward': 550,
            'creator_id': mike.id if mike else creator.id,
            'is_published': True,
            'is_approved': True,
            'rating': 4.6,
            'total_ratings': 54,
            'enrolled_count': 145,
            'modules': [
                {
                    'title': 'React Native Basics',
                    'description': 'Get started with React Native and Expo',
                    'order': 1,
                    'xp_reward': 80,
                    'resources': [
                        {'title': 'React Native Tutorial for Beginners', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=0-S5a0eXPoc', 'description': 'Full React Native course by Programming with Mosh'},
                        {'title': 'React Native in 100 Seconds', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=gvkqT_Uoahw', 'description': 'Quick overview by Fireship'},
                        {'title': 'Expo Documentation', 'type': 'article', 'url': 'https://docs.expo.dev/', 'description': 'Official Expo documentation for React Native'},
                    ],
                    'quiz': {
                        'title': 'React Native Basics Quiz',
                        'description': 'Test your React Native knowledge',
                        'passing_score': 70,
                        'xp_reward': 50,
                        'questions': [
                            {'text': 'React Native uses native components instead of web views.', 'type': 'true_false', 'options': ['True', 'False'], 'correct': 0, 'explanation': 'React Native renders using actual native components, not WebViews.', 'points': 10},
                            {'text': 'Which component is the React Native equivalent of <div>?', 'type': 'multiple_choice', 'options': ['<Container>', '<View>', '<Box>', '<Section>'], 'correct': 1, 'explanation': '<View> is the fundamental building block in React Native, similar to <div> in HTML.', 'points': 10},
                        ]
                    }
                },
            ]
        },
    ]

    for path_data in paths_data:
        if LearningPath.query.filter_by(title=path_data['title']).first():
            continue
        
        modules_data = path_data.pop('modules')
        path = LearningPath(**path_data)
        db.session.add(path)
        db.session.flush()

        for mod_data in modules_data:
            resources_data = mod_data.pop('resources')
            quiz_data = mod_data.pop('quiz', None)
            mod_data['learning_path_id'] = path.id
            module = Module(**mod_data)
            db.session.add(module)
            db.session.flush()

            for i, res in enumerate(resources_data):
                resource = Resource(
                    title=res['title'],
                    description=res.get('description', ''),
                    resource_type=res['type'],
                    url=res['url'],
                    order=i + 1,
                    module_id=module.id
                )
                db.session.add(resource)

            if quiz_data:
                questions_data = quiz_data.pop('questions')
                quiz = Quiz(
                    title=quiz_data['title'],
                    description=quiz_data['description'],
                    module_id=module.id,
                    passing_score=quiz_data['passing_score'],
                    xp_reward=quiz_data['xp_reward']
                )
                db.session.add(quiz)
                db.session.flush()

                for j, q in enumerate(questions_data):
                    question = Question(
                        quiz_id=quiz.id,
                        question_text=q['text'],
                        question_type=q['type'],
                        correct_answer=q['correct'],
                        explanation=q['explanation'],
                        order=j + 1,
                        points=q['points']
                    )
                    question.set_options(q['options'])
                    db.session.add(question)

    db.session.commit()
    print(f"Created {len(paths_data)} learning paths with modules, resources, and quizzes")


def seed_all():
    print("Seeding database...")
    seed_badges()
    seed_achievements()
    seed_challenges()
    seed_users()
    seed_learning_paths()
    print("Database seeding complete!")


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_all()
