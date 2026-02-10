from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.quiz import Quiz, Question, QuizAttempt
from app.models.learning_path import Module
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

quizzes_bp = Blueprint('quizzes', __name__)


@quizzes_bp.route('/module/<int:module_id>/quiz', methods=['GET'])
def get_module_quiz(module_id):
    """Get quiz for a specific module."""
    module = Module.query.get(module_id)
    if not module:
        return jsonify({'error': 'Module not found'}), 404
    
    quiz = Quiz.query.filter_by(module_id=module_id).first()
    if not quiz:
        return jsonify({'error': 'No quiz found for this module'}), 404
    
    # Don't include correct answers in the response
    quiz_data = quiz.to_dict(include_questions=True)
    for q in quiz_data.get('questions', []):
        q.pop('correct_answer', None)
        q.pop('explanation', None)
    
    return jsonify({
        'success': True,
        'data': {'quiz': quiz_data}
    }), 200


@quizzes_bp.route('/<int:quiz_id>', methods=['GET'])
def get_quiz(quiz_id):
    """Get a specific quiz by ID."""
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
    quiz_data = quiz.to_dict(include_questions=True)
    for q in quiz_data.get('questions', []):
        q.pop('correct_answer', None)
        q.pop('explanation', None)
    
    return jsonify({
        'success': True,
        'data': {'quiz': quiz_data}
    }), 200


@quizzes_bp.route('/<int:quiz_id>/submit', methods=['POST'])
@jwt_required()
def submit_quiz(quiz_id):
    """Submit quiz answers and get results."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
    data = request.get_json()
    if not data or 'answers' not in data:
        return jsonify({'error': 'Answers are required'}), 400
    
    user_answers = data.get('answers', [])  # [{question_id: X, answer: Y}, ...]
    time_taken = data.get('time_taken', 0)
    
    # Grade the quiz
    questions = quiz.questions.all()
    correct_count = 0
    total_points = 0
    max_points = 0
    results = []
    
    for question in questions:
        max_points += question.points
        user_answer = next(
            (a for a in user_answers if a.get('question_id') == question.id),
            None
        )
        
        if user_answer:
            is_correct = user_answer.get('answer') == question.correct_answer
            if is_correct:
                correct_count += 1
                total_points += question.points
            
            results.append({
                'question_id': question.id,
                'user_answer': user_answer.get('answer'),
                'correct_answer': question.correct_answer,
                'is_correct': is_correct,
                'explanation': question.explanation,
                'points_earned': question.points if is_correct else 0
            })
    
    # Calculate score
    score = int((correct_count / len(questions) * 100)) if questions else 0
    passed = score >= quiz.passing_score
    
    # Calculate XP earned
    xp_earned = 0
    if passed:
        xp_earned = quiz.xp_reward
        if score == 100:
            xp_earned += 25  # Perfect score bonus
        
        # Add XP to user
        user.xp += xp_earned
        user.points += total_points
    
    # Create quiz attempt record
    attempt = QuizAttempt(
        user_id=user_id,
        quiz_id=quiz_id,
        score=score,
        correct_answers=correct_count,
        total_questions=len(questions),
        passed=passed,
        xp_earned=xp_earned,
        time_taken=time_taken,
        completed_at=datetime.utcnow()
    )
    attempt.set_answers(user_answers)
    
    db.session.add(attempt)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': {
            'score': score,
            'passed': passed,
            'correct_answers': correct_count,
            'total_questions': len(questions),
            'xp_earned': xp_earned,
            'points_earned': total_points,
            'results': results,
            'attempt_id': attempt.id
        }
    }), 200


@quizzes_bp.route('/<int:quiz_id>/attempts', methods=['GET'])
@jwt_required()
def get_quiz_attempts(quiz_id):
    """Get user's attempts for a specific quiz."""
    user_id = get_jwt_identity()
    
    attempts = QuizAttempt.query.filter_by(
        user_id=user_id,
        quiz_id=quiz_id
    ).order_by(QuizAttempt.completed_at.desc()).all()
    
    return jsonify({
        'success': True,
        'data': {'attempts': [a.to_dict() for a in attempts]},
        'count': len(attempts)
    }), 200


@quizzes_bp.route('/attempts/me', methods=['GET'])
@jwt_required()
def get_my_attempts():
    """Get all quiz attempts for the current user."""
    user_id = get_jwt_identity()
    
    attempts = QuizAttempt.query.filter_by(
        user_id=user_id
    ).order_by(QuizAttempt.completed_at.desc()).limit(20).all()
    
    return jsonify({
        'success': True,
        'data': {'attempts': [a.to_dict() for a in attempts]},
        'count': len(attempts)
    }), 200
