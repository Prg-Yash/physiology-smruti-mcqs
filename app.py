"""
Flask Web Application for MCQ Quiz
Beautiful, clean interface with category selection and scoring
"""

from flask import Flask, render_template, jsonify, request, session
import json
import random
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# Load MCQ data
def load_mcqs():
    """Load MCQs from JSON file"""
    try:
        with open('mcqs_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('mcqs', {})
    except FileNotFoundError:
        return {}

MCQ_DATA = load_mcqs()

@app.route('/')
def index():
    """Home page with category selection"""
    categories = list(MCQ_DATA.keys())
    category_stats = {cat: len(MCQ_DATA[cat]) for cat in categories}
    return render_template('index.html', 
                         categories=categories,
                         category_stats=category_stats)

@app.route('/quiz/<category>')
def quiz(category):
    """Quiz page for selected category"""
    if category not in MCQ_DATA:
        return "Category not found", 404
    
    # Initialize session for this quiz
    session['category'] = category
    session['current_question'] = 0
    session['score'] = 0
    session['answers'] = []
    session['start_time'] = datetime.now().isoformat()
    
    return render_template('quiz.html', category=category)

@app.route('/api/question/<category>/<int:question_num>')
def get_question(category, question_num):
    """Get specific question from category"""
    if category not in MCQ_DATA:
        return jsonify({'error': 'Category not found'}), 404
    
    questions = MCQ_DATA[category]
    if question_num >= len(questions):
        return jsonify({'error': 'Question not found'}), 404
    
    question = questions[question_num]
    
    return jsonify({
        'question': question['question'],
        'options': question['options'],
        'question_num': question_num,
        'total_questions': len(questions)
    })

@app.route('/api/check_answer', methods=['POST'])
def check_answer():
    """Check if answer is correct"""
    data = request.json
    category = data.get('category')
    question_num = data.get('question_num')
    selected_answer = data.get('selected_answer')
    
    if category not in MCQ_DATA:
        return jsonify({'error': 'Category not found'}), 404
    
    questions = MCQ_DATA[category]
    if question_num >= len(questions):
        return jsonify({'error': 'Question not found'}), 404
    
    question = questions[question_num]
    correct_answer = question.get('correct_answer')
    is_correct = selected_answer == correct_answer
    
    # Update session
    if 'answers' not in session:
        session['answers'] = []
    
    session['answers'].append({
        'question_num': question_num,
        'selected': selected_answer,
        'correct': correct_answer,
        'is_correct': is_correct
    })
    
    if is_correct:
        session['score'] = session.get('score', 0) + 1
    
    session.modified = True
    
    return jsonify({
        'is_correct': is_correct,
        'correct_answer': correct_answer,
        'explanation': question.get('explanation', '')
    })

@app.route('/api/results/<category>')
def get_results(category):
    """Get quiz results"""
    if category not in MCQ_DATA:
        return jsonify({'error': 'Category not found'}), 404
    
    total_questions = len(MCQ_DATA[category])
    score = session.get('score', 0)
    answers = session.get('answers', [])
    
    percentage = (score / total_questions * 100) if total_questions > 0 else 0
    
    return jsonify({
        'score': score,
        'total': total_questions,
        'percentage': round(percentage, 2),
        'answers': answers
    })

@app.route('/results/<category>')
def results(category):
    """Results page"""
    if category not in MCQ_DATA:
        return "Category not found", 404
    
    return render_template('results.html', category=category)

@app.route('/api/categories')
def get_categories():
    """Get all categories with stats"""
    categories = []
    for cat, questions in MCQ_DATA.items():
        categories.append({
            'name': cat,
            'question_count': len(questions)
        })
    return jsonify(categories)

if __name__ == '__main__':
    if not MCQ_DATA:
        print("Warning: No MCQ data found!")
        print("Please run extract_mcqs_improved.py first to generate mcqs_data.json")
    else:
        print(f"Loaded {sum(len(q) for q in MCQ_DATA.values())} questions from {len(MCQ_DATA)} categories")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
