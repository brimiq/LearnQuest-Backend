"""
Database seed script for LearnQuest
Run this after initializing the database to populate with test data.
Usage: python seed.py
"""

from app import create_app, db
from app.models.user import User
from app.models.learning_path import LearningPath, Module, Resource
from app.models.gamification import Badge, Achievement, Challenge
from datetime import datetime, timedelta

def seed_database():
    app = create_app()
    
    with app.app_context():
        print("🌱 Starting database seeding...")
        
        # Clear existing data (optional - comment out if you want to keep data)
        print("  Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create users with different roles
        print("  Creating users...")
        
        admin = User(
            username="admin",
            email="admin@learnquest.com",
            role="admin",
            xp=5000,
            points=2500,
            streak_days=30,
            hours_learned=100.0,
            bio="Platform administrator"
        )
        admin.set_password("admin123")
        
        contributor = User(
            username="teacher_jane",
            email="jane@learnquest.com",
            role="contributor",
            xp=3500,
            points=1800,
            streak_days=15,
            hours_learned=60.0,
            bio="Passionate educator and course creator"
        )
        contributor.set_password("teacher123")
        
        learner = User(
            username="student_john",
            email="john@learnquest.com",
            role="learner",
            xp=1200,
            points=600,
            streak_days=7,
            hours_learned=25.5,
            bio="Eager learner exploring new technologies"
        )
        learner.set_password("student123")
        
        learner2 = User(
            username="alice_dev",
            email="alice@example.com",
            role="learner",
            xp=800,
            points=400,
            streak_days=3,
            hours_learned=12.0,
            bio="Aspiring full-stack developer"
        )
        learner2.set_password("alice123")
        
        db.session.add_all([admin, contributor, learner, learner2])
        db.session.commit()
        
        # Create badges
        print("  Creating badges...")
        badges = [
            Badge(name="First Steps", description="Complete your first module", badge_type="bronze", icon_url="🎯"),
            Badge(name="Week Warrior", description="Maintain a 7-day streak", badge_type="silver", icon_url="🔥"),
            Badge(name="Month Master", description="Maintain a 30-day streak", badge_type="gold", icon_url="⭐"),
            Badge(name="Path Pioneer", description="Complete your first learning path", badge_type="silver", icon_url="🏆"),
            Badge(name="Knowledge Sharer", description="Create your first resource", badge_type="bronze", icon_url="📚"),
            Badge(name="Community Star", description="Receive 10 ratings on your content", badge_type="gold", icon_url="💫"),
        ]
        db.session.add_all(badges)
        db.session.commit()
        
        # Create achievements
        print("  Creating achievements...")
        achievements = [
            Achievement(name="Quick Learner", description="Complete 5 modules", xp_reward=100, requirement_type="modules_completed", requirement_value=5),
            Achievement(name="Dedicated Student", description="Complete 10 modules", xp_reward=250, requirement_type="modules_completed", requirement_value=10),
            Achievement(name="Path Completer", description="Complete 3 learning paths", xp_reward=500, requirement_type="paths_completed", requirement_value=3),
            Achievement(name="Streak Champion", description="Maintain a 14-day streak", xp_reward=200, requirement_type="streak", requirement_value=14),
        ]
        db.session.add_all(achievements)
        db.session.commit()
        
        # Create challenges
        print("  Creating challenges...")
        now = datetime.utcnow()
        challenges = [
            Challenge(
                title="Weekly Warrior",
                description="Complete 5 modules this week",
                challenge_type="weekly",
                xp_reward=150,
                points_reward=75,
                requirement_type="modules_completed",
                requirement_value=5,
                start_date=now,
                end_date=now + timedelta(days=7),
                is_active=True
            ),
            Challenge(
                title="February Learning Sprint",
                description="Complete 2 learning paths this month",
                challenge_type="monthly",
                xp_reward=500,
                points_reward=250,
                requirement_type="paths_completed",
                requirement_value=2,
                start_date=now,
                end_date=now + timedelta(days=30),
                is_active=True
            ),
        ]
        db.session.add_all(challenges)
        db.session.commit()
        
        # Create learning paths with modules and resources
        print("  Creating learning paths...")
        
        # Learning Path 1: Web Development
        web_dev_path = LearningPath(
            title="Full Stack Web Development",
            description="Learn to build modern web applications from scratch using HTML, CSS, JavaScript, and React.",
            category="Development",
            difficulty="beginner",
            image_url="https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=500&h=300&fit=crop",
            xp_reward=500,
            creator_id=contributor.id,
            is_published=True,
            is_approved=True,
            rating=4.5,
            total_ratings=24,
            enrolled_count=156
        )
        db.session.add(web_dev_path)
        db.session.commit()
        
        # Modules for Web Development
        modules_web = [
            Module(title="HTML Fundamentals", description="Learn the basics of HTML structure and elements", order=1, xp_reward=50, learning_path_id=web_dev_path.id),
            Module(title="CSS Styling", description="Master CSS for beautiful web designs", order=2, xp_reward=50, learning_path_id=web_dev_path.id),
            Module(title="JavaScript Basics", description="Introduction to programming with JavaScript", order=3, xp_reward=75, learning_path_id=web_dev_path.id),
            Module(title="React Introduction", description="Build interactive UIs with React", order=4, xp_reward=100, learning_path_id=web_dev_path.id),
        ]
        db.session.add_all(modules_web)
        db.session.commit()
        
        # Resources for first module
        resources_html = [
            Resource(title="What is HTML?", description="Introduction to HTML", resource_type="article", url="https://developer.mozilla.org/en-US/docs/Web/HTML", order=1, module_id=modules_web[0].id),
            Resource(title="HTML Tags Explained", description="Video walkthrough of common HTML tags", resource_type="video", url="https://www.youtube.com/watch?v=UB1O30fR-EE", order=2, module_id=modules_web[0].id),
            Resource(title="HTML Quiz", description="Test your HTML knowledge", resource_type="quiz", content='{"questions": [{"q": "What does HTML stand for?", "options": ["Hyper Text Markup Language", "High Tech Modern Language"], "answer": 0}]}', order=3, module_id=modules_web[0].id),
        ]
        db.session.add_all(resources_html)
        
        # Learning Path 2: UX Design
        ux_path = LearningPath(
            title="UX Design Principles",
            description="Master the fundamentals of user experience design and create intuitive interfaces.",
            category="Design",
            difficulty="intermediate",
            image_url="https://images.unsplash.com/photo-1558655146-d09347e0b7a9?w=500&h=300&fit=crop",
            xp_reward=400,
            creator_id=contributor.id,
            is_published=True,
            is_approved=True,
            rating=4.8,
            total_ratings=18,
            enrolled_count=89
        )
        db.session.add(ux_path)
        db.session.commit()
        
        modules_ux = [
            Module(title="Design Thinking", description="Learn the design thinking process", order=1, xp_reward=60, learning_path_id=ux_path.id),
            Module(title="User Research", description="Understand your users through research", order=2, xp_reward=60, learning_path_id=ux_path.id),
            Module(title="Wireframing", description="Create low-fidelity designs", order=3, xp_reward=70, learning_path_id=ux_path.id),
        ]
        db.session.add_all(modules_ux)
        
        # Learning Path 3: Data Science
        data_path = LearningPath(
            title="Introduction to Data Science",
            description="Start your journey into data science with Python and machine learning basics.",
            category="Data Science",
            difficulty="beginner",
            image_url="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500&h=300&fit=crop",
            xp_reward=450,
            creator_id=admin.id,
            is_published=True,
            is_approved=True,
            rating=4.6,
            total_ratings=32,
            enrolled_count=210
        )
        db.session.add(data_path)
        db.session.commit()
        
        modules_data = [
            Module(title="Python Basics", description="Learn Python programming fundamentals", order=1, xp_reward=50, learning_path_id=data_path.id),
            Module(title="Data Analysis with Pandas", description="Analyze data using Pandas library", order=2, xp_reward=75, learning_path_id=data_path.id),
            Module(title="Data Visualization", description="Create compelling visualizations", order=3, xp_reward=75, learning_path_id=data_path.id),
            Module(title="Intro to Machine Learning", description="Basic ML concepts and algorithms", order=4, xp_reward=100, learning_path_id=data_path.id),
        ]
        db.session.add_all(modules_data)
        
        db.session.commit()
        
        print("\n✅ Database seeded successfully!")
        print("\n📋 Test Accounts:")
        print("  ┌─────────────────────────────────────────────────┐")
        print("  │ Role        │ Email                  │ Password │")
        print("  ├─────────────────────────────────────────────────┤")
        print("  │ Admin       │ admin@learnquest.com   │ admin123 │")
        print("  │ Contributor │ jane@learnquest.com    │ teacher123│")
        print("  │ Learner     │ john@learnquest.com    │ student123│")
        print("  │ Learner     │ alice@example.com      │ alice123 │")
        print("  └─────────────────────────────────────────────────┘")

if __name__ == "__main__":
    seed_database()
