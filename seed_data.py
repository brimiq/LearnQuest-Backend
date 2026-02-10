"""
Seed data for LearnQuest database.
Run with: python seed_data.py
"""
from app import create_app, db
from app.models import (
    User, Badge, Achievement, Challenge, 
    LearningPath, Module, Resource,
    Quiz, Question
)
from datetime import datetime, timedelta
import json


def seed_badges():
    """Create initial badges."""
    badges = [
        {
            'name': 'Early Bird',
            'description': 'Complete a lesson before 8 AM',
            'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=sun&backgroundColor=ffd700',
            'badge_type': 'bronze',
            'is_seasonal': False
        },
        {
            'name': 'Week Warrior',
            'description': 'Maintain a 7-day learning streak',
            'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=fire&backgroundColor=ff6b35',
            'badge_type': 'silver',
            'is_seasonal': False
        },
        {
            'name': 'Quiz Master',
            'description': 'Score 100% on 5 quizzes',
            'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=brain&backgroundColor=9333ea',
            'badge_type': 'gold',
            'is_seasonal': False
        },
        {
            'name': 'Social Butterfly',
            'description': 'Post 10 helpful comments',
            'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=chat&backgroundColor=06b6d4',
            'badge_type': 'bronze',
            'is_seasonal': False
        },
        {
            'name': 'Code Ninja',
            'description': 'Complete 50 coding challenges',
            'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=code&backgroundColor=22c55e',
            'badge_type': 'platinum',
            'is_seasonal': False
        },
        {
            'name': 'Mentor',
            'description': 'Help 10 other learners',
            'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=heart&backgroundColor=ec4899',
            'badge_type': 'gold',
            'is_seasonal': False
        },
        {
            'name': 'First Steps',
            'description': 'Complete your first lesson',
            'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=rocket&backgroundColor=3b82f6',
            'badge_type': 'bronze',
            'is_seasonal': False
        },
        {
            'name': 'Path Finder',
            'description': 'Complete your first learning path',
            'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=map&backgroundColor=10b981',
            'badge_type': 'silver',
            'is_seasonal': False
        },
        {
            'name': 'Data Science Month',
            'description': 'Complete 3 data science paths in March',
            'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=chart&backgroundColor=f59e0b',
            'badge_type': 'special',
            'is_seasonal': True
        },
        {
            'name': 'Streak Legend',
            'description': 'Maintain a 30-day learning streak',
            'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=flame&backgroundColor=ef4444',
            'badge_type': 'platinum',
            'is_seasonal': False
        }
    ]
    
    for badge_data in badges:
        existing = Badge.query.filter_by(name=badge_data['name']).first()
        if not existing:
            badge = Badge(**badge_data)
            db.session.add(badge)
    
    db.session.commit()
    print(f"Created {len(badges)} badges")


def seed_achievements():
    """Create achievements."""
    achievements = [
        {
            'name': 'Getting Started',
            'description': 'Complete your first module',
            'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=star&backgroundColor=ffd700',
            'xp_reward': 50,
            'points_reward': 25,
            'requirement_type': 'modules_completed',
            'requirement_value': 1
        },
        {
            'name': 'Dedicated Learner',
            'description': 'Complete 10 modules',
            'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=trophy&backgroundColor=f59e0b',
            'xp_reward': 200,
            'points_reward': 100,
            'requirement_type': 'modules_completed',
            'requirement_value': 10
        },
        {
            'name': 'Path Master',
            'description': 'Complete 5 learning paths',
            'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=crown&backgroundColor=9333ea',
            'xp_reward': 500,
            'points_reward': 250,
            'requirement_type': 'paths_completed',
            'requirement_value': 5
        },
        {
            'name': 'Streak Starter',
            'description': 'Maintain a 3-day streak',
            'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=fire&backgroundColor=ef4444',
            'xp_reward': 30,
            'points_reward': 15,
            'requirement_type': 'streak',
            'requirement_value': 3
        },
        {
            'name': 'Knowledge Seeker',
            'description': 'Earn 1000 XP',
            'icon_url': 'https://api.dicebear.com/7.x/icons/svg?seed=gem&backgroundColor=06b6d4',
            'xp_reward': 100,
            'points_reward': 50,
            'requirement_type': 'xp_earned',
            'requirement_value': 1000
        }
    ]
    
    for ach_data in achievements:
        existing = Achievement.query.filter_by(name=ach_data['name']).first()
        if not existing:
            achievement = Achievement(**ach_data)
            db.session.add(achievement)
    
    db.session.commit()
    print(f"Created {len(achievements)} achievements")


def seed_challenges():
    """Create active challenges."""
    now = datetime.utcnow()
    challenges = [
        {
            'title': 'CSS Grid Master',
            'description': 'Complete the CSS Grid layout module and score at least 80% on the quiz.',
            'challenge_type': 'weekly',
            'xp_reward': 150,
            'points_reward': 75,
            'requirement_type': 'quiz_score',
            'requirement_value': 80,
            'start_date': now,
            'end_date': now + timedelta(days=7),
            'is_active': True
        },
        {
            'title': 'React Fundamentals Sprint',
            'description': 'Complete 3 React modules in one week.',
            'challenge_type': 'weekly',
            'xp_reward': 200,
            'points_reward': 100,
            'requirement_type': 'modules_completed',
            'requirement_value': 3,
            'start_date': now,
            'end_date': now + timedelta(days=7),
            'is_active': True
        },
        {
            'title': 'Python Marathon',
            'description': 'Complete the entire Python Basics learning path.',
            'challenge_type': 'monthly',
            'xp_reward': 500,
            'points_reward': 250,
            'requirement_type': 'path_completed',
            'requirement_value': 1,
            'start_date': now,
            'end_date': now + timedelta(days=30),
            'is_active': True
        },
        {
            'title': 'Community Helper',
            'description': 'Post 5 helpful comments on learning resources.',
            'challenge_type': 'weekly',
            'xp_reward': 100,
            'points_reward': 50,
            'requirement_type': 'comments_posted',
            'requirement_value': 5,
            'start_date': now,
            'end_date': now + timedelta(days=7),
            'is_active': True
        }
    ]
    
    for ch_data in challenges:
        existing = Challenge.query.filter_by(title=ch_data['title']).first()
        if not existing:
            challenge = Challenge(**ch_data)
            db.session.add(challenge)
    
    db.session.commit()
    print(f"Created {len(challenges)} challenges")


def seed_learning_paths():
    """Create sample learning paths with modules, resources, and quizzes."""
    
    # First, create a demo user as creator
    demo_user = User.query.filter_by(username='demo_creator').first()
    if not demo_user:
        demo_user = User(
            username='demo_creator',
            email='creator@learnquest.com',
            role='contributor',
            xp=5000,
            points=2500,
            streak_days=15,
            hours_learned=48.5,
            avatar_url='https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=200&h=200&fit=crop',
            bio='Senior developer and educator passionate about teaching.'
        )
        demo_user.set_password('demo123')
        db.session.add(demo_user)
        db.session.commit()
    
    learning_paths_data = [
        {
            'title': 'Full Stack Web Development',
            'description': 'Master modern web development from frontend to backend. Learn React, Node.js, databases, and deployment.',
            'category': 'Development',
            'difficulty': 'intermediate',
            'image_url': 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800&h=400&fit=crop',
            'xp_reward': 500,
            'is_published': True,
            'is_approved': True,
            'rating': 4.8,
            'enrolled_count': 2450,
            'modules': [
                {
                    'title': 'Module 1: HTML & CSS Foundations',
                    'description': 'Learn the building blocks of the web.',
                    'xp_reward': 75,
                    'resources': [
                        {'title': 'Introduction to HTML', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=qz0aGYrrlhU'},
                        {'title': 'CSS Box Model Explained', 'type': 'article', 'url': 'https://developer.mozilla.org/en-US/docs/Learn/CSS/Building_blocks/The_box_model'},
                        {'title': 'Flexbox Tutorial', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=JJSoEo8JSnc'},
                    ],
                    'quiz': {
                        'title': 'HTML & CSS Quiz',
                        'passing_score': 70,
                        'questions': [
                            {'text': 'What does HTML stand for?', 'options': ['Hyper Text Markup Language', 'High Tech Modern Language', 'Hyper Transfer Markup Language', 'Home Tool Markup Language'], 'correct': 0, 'explanation': 'HTML stands for Hyper Text Markup Language.'},
                            {'text': 'Which CSS property is used to change text color?', 'options': ['text-color', 'font-color', 'color', 'text-style'], 'correct': 2, 'explanation': 'The color property is used to set the text color.'},
                            {'text': 'What is the correct HTML element for the largest heading?', 'options': ['<heading>', '<h6>', '<head>', '<h1>'], 'correct': 3, 'explanation': '<h1> defines the most important heading.'},
                            {'text': 'Which property is used to add space inside an element?', 'options': ['margin', 'padding', 'spacing', 'border'], 'correct': 1, 'explanation': 'Padding adds space inside an element, between its content and border.'},
                            {'text': 'How do you select an element with id "demo"?', 'options': ['.demo', '#demo', 'demo', '*demo'], 'correct': 1, 'explanation': 'The # symbol is used to select elements by ID in CSS.'},
                        ]
                    }
                },
                {
                    'title': 'Module 2: JavaScript Essentials',
                    'description': 'Master JavaScript fundamentals and ES6+ features.',
                    'xp_reward': 100,
                    'resources': [
                        {'title': 'JavaScript Basics', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=W6NZfCO5SIk'},
                        {'title': 'ES6 Features Overview', 'type': 'article', 'url': 'https://www.freecodecamp.org/news/javascript-es6-tutorial/'},
                        {'title': 'Async/Await Explained', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=V_Kr9OSfDeU'},
                    ],
                    'quiz': {
                        'title': 'JavaScript Quiz',
                        'passing_score': 70,
                        'questions': [
                            {'text': 'Which keyword declares a block-scoped variable?', 'options': ['var', 'let', 'const', 'Both let and const'], 'correct': 3, 'explanation': 'Both let and const declare block-scoped variables.'},
                            {'text': 'What is the output of typeof []?', 'options': ['array', 'object', 'list', 'undefined'], 'correct': 1, 'explanation': 'Arrays in JavaScript are technically objects.'},
                            {'text': 'Which method adds an element to the end of an array?', 'options': ['push()', 'pop()', 'shift()', 'unshift()'], 'correct': 0, 'explanation': 'push() adds elements to the end of an array.'},
                            {'text': 'What does === check for?', 'options': ['Value only', 'Type only', 'Value and type', 'Reference'], 'correct': 2, 'explanation': '=== checks for both value and type equality.'},
                            {'text': 'What is a closure?', 'options': ['A way to close browser tabs', 'A function with access to its outer scope', 'A type of loop', 'An error type'], 'correct': 1, 'explanation': 'A closure is a function that has access to variables from its outer (enclosing) scope.'},
                        ]
                    }
                },
                {
                    'title': 'Module 3: React Fundamentals',
                    'description': 'Build modern UIs with React.',
                    'xp_reward': 125,
                    'resources': [
                        {'title': 'React in 100 Seconds', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=Tn6-PIqc4UM'},
                        {'title': 'React Hooks Tutorial', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=TNhaISOUy6Q'},
                        {'title': 'State Management with Context', 'type': 'article', 'url': 'https://react.dev/learn/passing-data-deeply-with-context'},
                    ],
                    'quiz': {
                        'title': 'React Quiz',
                        'passing_score': 70,
                        'questions': [
                            {'text': 'What hook is used to manage state in functional components?', 'options': ['useEffect', 'useState', 'useContext', 'useReducer'], 'correct': 1, 'explanation': 'useState is the primary hook for managing state.'},
                            {'text': 'What does JSX stand for?', 'options': ['JavaScript XML', 'Java Syntax Extension', 'JSON XML', 'JavaScript Extension'], 'correct': 0, 'explanation': 'JSX stands for JavaScript XML.'},
                            {'text': 'When does useEffect run by default?', 'options': ['Only on mount', 'Only on unmount', 'After every render', 'Never'], 'correct': 2, 'explanation': 'By default, useEffect runs after every render.'},
                            {'text': 'What is the virtual DOM?', 'options': ['A browser feature', 'A lightweight copy of the real DOM', 'A CSS framework', 'A testing tool'], 'correct': 1, 'explanation': 'The virtual DOM is a lightweight JavaScript representation of the actual DOM.'},
                            {'text': 'How do you pass data from parent to child?', 'options': ['State', 'Props', 'Context', 'Redux'], 'correct': 1, 'explanation': 'Props are used to pass data from parent to child components.'},
                        ]
                    }
                }
            ]
        },
        {
            'title': 'Python for Data Science',
            'description': 'Learn Python programming and data analysis with pandas, NumPy, and visualization libraries.',
            'category': 'Data Science',
            'difficulty': 'beginner',
            'image_url': 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=800&h=400&fit=crop',
            'xp_reward': 400,
            'is_published': True,
            'is_approved': True,
            'rating': 4.9,
            'enrolled_count': 3200,
            'modules': [
                {
                    'title': 'Module 1: Python Basics',
                    'description': 'Get started with Python programming.',
                    'xp_reward': 50,
                    'resources': [
                        {'title': 'Python for Beginners', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=kqtD5dpn9C8'},
                        {'title': 'Python Documentation', 'type': 'article', 'url': 'https://docs.python.org/3/tutorial/'},
                    ],
                    'quiz': {
                        'title': 'Python Basics Quiz',
                        'passing_score': 70,
                        'questions': [
                            {'text': 'What is the correct way to create a list in Python?', 'options': ['list = (1, 2, 3)', 'list = [1, 2, 3]', 'list = {1, 2, 3}', 'list = <1, 2, 3>'], 'correct': 1, 'explanation': 'Lists are created using square brackets [].'},
                            {'text': 'Which keyword is used to define a function?', 'options': ['function', 'def', 'func', 'define'], 'correct': 1, 'explanation': 'The def keyword is used to define functions in Python.'},
                            {'text': 'How do you start a comment in Python?', 'options': ['//', '/*', '#', '--'], 'correct': 2, 'explanation': 'Python uses # for single-line comments.'},
                            {'text': 'What is the output of print(2 ** 3)?', 'options': ['5', '6', '8', '9'], 'correct': 2, 'explanation': '** is the exponentiation operator. 2^3 = 8'},
                            {'text': 'Which method adds an item to the end of a list?', 'options': ['add()', 'append()', 'insert()', 'push()'], 'correct': 1, 'explanation': 'append() adds an item to the end of a list.'},
                        ]
                    }
                },
                {
                    'title': 'Module 2: Data Analysis with Pandas',
                    'description': 'Master data manipulation with pandas.',
                    'xp_reward': 75,
                    'resources': [
                        {'title': 'Pandas Tutorial', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=vmEHCJofslg'},
                        {'title': 'Pandas Documentation', 'type': 'article', 'url': 'https://pandas.pydata.org/docs/getting_started/'},
                    ],
                    'quiz': {
                        'title': 'Pandas Quiz',
                        'passing_score': 70,
                        'questions': [
                            {'text': 'What is a DataFrame?', 'options': ['A 1D array', 'A 2D labeled data structure', 'A dictionary', 'A function'], 'correct': 1, 'explanation': 'A DataFrame is a 2-dimensional labeled data structure.'},
                            {'text': 'How do you read a CSV file?', 'options': ['pd.read_csv()', 'pd.load_csv()', 'pd.open_csv()', 'pd.import_csv()'], 'correct': 0, 'explanation': 'pd.read_csv() is used to read CSV files into a DataFrame.'},
                            {'text': 'How do you select a column named "age"?', 'options': ['df.age or df["age"]', 'df.get("age")', 'df.column("age")', 'df.select("age")'], 'correct': 0, 'explanation': 'You can use dot notation or bracket notation to select columns.'},
                        ]
                    }
                }
            ]
        },
        {
            'title': 'UX Design Fundamentals',
            'description': 'Learn user experience design principles, research methods, and prototyping techniques.',
            'category': 'Design',
            'difficulty': 'beginner',
            'image_url': 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=800&h=400&fit=crop',
            'xp_reward': 350,
            'is_published': True,
            'is_approved': True,
            'rating': 4.7,
            'enrolled_count': 1850,
            'modules': [
                {
                    'title': 'Module 1: Introduction to UX',
                    'description': 'Understand the fundamentals of user experience design.',
                    'xp_reward': 50,
                    'resources': [
                        {'title': 'What is UX Design?', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=SRec90j6lTY'},
                        {'title': 'UX Design Principles', 'type': 'article', 'url': 'https://www.interaction-design.org/literature/topics/ux-design'},
                    ],
                    'quiz': {
                        'title': 'UX Fundamentals Quiz',
                        'passing_score': 70,
                        'questions': [
                            {'text': 'What does UX stand for?', 'options': ['User Experience', 'User Extension', 'Universal Experience', 'Unified Experience'], 'correct': 0, 'explanation': 'UX stands for User Experience.'},
                            {'text': 'Which is NOT a UX research method?', 'options': ['User interviews', 'A/B testing', 'Database optimization', 'Usability testing'], 'correct': 2, 'explanation': 'Database optimization is a backend development task, not a UX research method.'},
                            {'text': 'What is a persona?', 'options': ['A user type', 'A fictional character representing users', 'A design tool', 'A testing method'], 'correct': 1, 'explanation': 'A persona is a fictional character created to represent a user type.'},
                        ]
                    }
                }
            ]
        },
        {
            'title': 'DevOps Essentials',
            'description': 'Master CI/CD pipelines, containerization with Docker, and cloud deployment.',
            'category': 'DevOps',
            'difficulty': 'advanced',
            'image_url': 'https://images.unsplash.com/photo-1667372393119-3d4c48d07fc9?w=800&h=400&fit=crop',
            'xp_reward': 600,
            'is_published': True,
            'is_approved': True,
            'rating': 4.6,
            'enrolled_count': 980,
            'modules': [
                {
                    'title': 'Module 1: Docker Fundamentals',
                    'description': 'Learn containerization with Docker.',
                    'xp_reward': 100,
                    'resources': [
                        {'title': 'Docker in 100 Seconds', 'type': 'video', 'url': 'https://www.youtube.com/watch?v=Gjnup-PuquQ'},
                        {'title': 'Docker Getting Started', 'type': 'article', 'url': 'https://docs.docker.com/get-started/'},
                    ],
                    'quiz': {
                        'title': 'Docker Quiz',
                        'passing_score': 70,
                        'questions': [
                            {'text': 'What is a Docker container?', 'options': ['A virtual machine', 'A lightweight isolated environment', 'A programming language', 'A database'], 'correct': 1, 'explanation': 'A container is a lightweight, isolated environment for running applications.'},
                            {'text': 'What file defines a Docker image?', 'options': ['docker.yml', 'Dockerfile', 'container.json', 'image.xml'], 'correct': 1, 'explanation': 'A Dockerfile contains instructions to build a Docker image.'},
                            {'text': 'What command runs a container?', 'options': ['docker start', 'docker run', 'docker execute', 'docker launch'], 'correct': 1, 'explanation': 'docker run creates and starts a container from an image.'},
                        ]
                    }
                }
            ]
        }
    ]
    
    for path_data in learning_paths_data:
        existing = LearningPath.query.filter_by(title=path_data['title']).first()
        if existing:
            continue
        
        modules_data = path_data.pop('modules', [])
        
        path = LearningPath(
            creator_id=demo_user.id,
            **path_data
        )
        db.session.add(path)
        db.session.flush()
        
        for order, mod_data in enumerate(modules_data):
            resources_data = mod_data.pop('resources', [])
            quiz_data = mod_data.pop('quiz', None)
            
            module = Module(
                learning_path_id=path.id,
                order=order,
                **mod_data
            )
            db.session.add(module)
            db.session.flush()
            
            for res_order, res_data in enumerate(resources_data):
                resource = Resource(
                    module_id=module.id,
                    title=res_data['title'],
                    resource_type=res_data['type'],
                    url=res_data['url'],
                    order=res_order
                )
                db.session.add(resource)
            
            if quiz_data:
                questions_data = quiz_data.pop('questions', [])
                quiz = Quiz(
                    module_id=module.id,
                    title=quiz_data['title'],
                    passing_score=quiz_data.get('passing_score', 70),
                    xp_reward=50
                )
                db.session.add(quiz)
                db.session.flush()
                
                for q_order, q_data in enumerate(questions_data):
                    question = Question(
                        quiz_id=quiz.id,
                        question_text=q_data['text'],
                        question_type='multiple_choice',
                        correct_answer=q_data['correct'],
                        explanation=q_data.get('explanation', ''),
                        order=q_order,
                        points=10
                    )
                    question.set_options(q_data['options'])
                    db.session.add(question)
    
    db.session.commit()
    print(f"Created {len(learning_paths_data)} learning paths with modules, resources, and quizzes")


def seed_demo_users():
    """Create demo users for testing."""
    users = [
        {
            'username': 'alex_learner',
            'email': 'alex@example.com',
            'role': 'learner',
            'xp': 12450,
            'points': 6225,
            'streak_days': 12,
            'hours_learned': 48.5,
            'avatar_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop',
            'bio': 'Passionate about learning web development!'
        },
        {
            'username': 'jessica_wong',
            'email': 'jessica@example.com',
            'role': 'contributor',
            'xp': 24500,
            'points': 12250,
            'streak_days': 45,
            'hours_learned': 156.0,
            'avatar_url': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&h=200&fit=crop',
            'bio': 'Full-stack developer and course creator.'
        },
        {
            'username': 'david_kim',
            'email': 'david@example.com',
            'role': 'learner',
            'xp': 22150,
            'points': 11075,
            'streak_days': 30,
            'hours_learned': 120.0,
            'avatar_url': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&h=200&fit=crop',
            'bio': 'Data scientist in training.'
        },
        {
            'username': 'sarah_jenkins',
            'email': 'sarah@example.com',
            'role': 'learner',
            'xp': 21800,
            'points': 10900,
            'streak_days': 28,
            'hours_learned': 98.0,
            'avatar_url': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200&h=200&fit=crop',
            'bio': 'UX designer learning to code.'
        },
        {
            'username': 'admin_user',
            'email': 'admin@learnquest.com',
            'role': 'admin',
            'xp': 50000,
            'points': 25000,
            'streak_days': 100,
            'hours_learned': 500.0,
            'avatar_url': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop',
            'bio': 'Platform administrator.'
        }
    ]
    
    for user_data in users:
        existing = User.query.filter_by(username=user_data['username']).first()
        if not existing:
            user = User(**user_data)
            user.set_password('demo123')
            db.session.add(user)
    
    db.session.commit()
    print(f"Created {len(users)} demo users")


def run_seed():
    """Run all seed functions."""
    print("Seeding database...")
    seed_badges()
    seed_achievements()
    seed_challenges()
    seed_demo_users()
    seed_learning_paths()
    print("Database seeding complete!")


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        run_seed()
