from app import db
from datetime import datetime
import json


class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    passing_score = db.Column(db.Integer, default=70)  # Percentage needed to pass
    xp_reward = db.Column(db.Integer, default=50)
    time_limit = db.Column(db.Integer, default=0)  # Minutes, 0 = no limit
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy='dynamic')
    
    def to_dict(self, include_questions=True):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'module_id': self.module_id,
            'passing_score': self.passing_score,
            'xp_reward': self.xp_reward,
            'time_limit': self.time_limit,
            'question_count': self.questions.count()
        }
        if include_questions:
            data['questions'] = [q.to_dict() for q in self.questions.order_by(Question.order).all()]
        return data


class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), default='multiple_choice')  # multiple_choice, true_false, code
    options = db.Column(db.Text)  # JSON array of options
    correct_answer = db.Column(db.Integer)  # Index of correct option (0-based)
    explanation = db.Column(db.Text)  # Explanation shown after answering
    order = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=10)
    
    def get_options(self):
        if self.options:
            return json.loads(self.options)
        return []
    
    def set_options(self, options_list):
        self.options = json.dumps(options_list)
    
    def to_dict(self, include_answer=False):
        data = {
            'id': self.id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'options': self.get_options(),
            'order': self.order,
            'points': self.points
        }
        if include_answer:
            data['correct_answer'] = self.correct_answer
            data['explanation'] = self.explanation
        return data


class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Integer, default=0)  # Percentage score
    correct_answers = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    passed = db.Column(db.Boolean, default=False)
    xp_earned = db.Column(db.Integer, default=0)
    answers = db.Column(db.Text)  # JSON of user's answers
    time_taken = db.Column(db.Integer, default=0)  # Seconds
    
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    user = db.relationship('User', backref='quiz_attempts')
    
    def get_answers(self):
        if self.answers:
            return json.loads(self.answers)
        return []
    
    def set_answers(self, answers_list):
        self.answers = json.dumps(answers_list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'quiz_id': self.quiz_id,
            'score': self.score,
            'correct_answers': self.correct_answers,
            'total_questions': self.total_questions,
            'passed': self.passed,
            'xp_earned': self.xp_earned,
            'time_taken': self.time_taken,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
