#!/usr/bin/env python3
"""
Question Improvement Web Application
A Flask-based web app that provides the complete question improvement pipeline.
"""

import json
import os
from typing import Dict, Optional

# Check if Flask is available
try:
    from flask import Flask, render_template, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    print("❌ Flask not installed. Install with: pip install flask")
    FLASK_AVAILABLE = False

# Import our question improvement functions
from simple_question_tester import (
    PROMPT_TEMPLATES,
    match_question_to_template_simple,
    transform_question_with_template_simple,
    calculate_metrics_for_text,
    should_polish_with_ollama,
    polish_low_scoring_questions
)

if FLASK_AVAILABLE:
    app = Flask(__name__)
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'

def get_question_types():
    """Get list of available question types for dropdown."""
    return list(PROMPT_TEMPLATES.keys())

def process_question_pipeline(question_text: str, question_type: Optional[str] = None) -> Dict:
    """
    Process a question through the complete pipeline.
    
    Args:
        question_text: The original question text
        question_type: Optional question type for targeted processing
        
    Returns:
        Dictionary with all pipeline results
    """
    # Calculate original metrics
    original_metrics = calculate_metrics_for_text(question_text)
    original_enhanced_score = sum([
        original_metrics['clarity'],
        original_metrics['conciseness'],
        original_metrics['technical_accuracy'],
        original_metrics['actionability']
    ]) / 4
    
    # Initialize results
    results = {
        'original_text': question_text,
        'original_metrics': original_metrics,
        'original_enhanced_score': original_enhanced_score,
        'template_matched': False,
        'template_improved_text': question_text,
        'template_metrics': original_metrics,
        'template_enhanced_score': original_enhanced_score,
        'ollama_used': False,
        'ollama_improved_text': question_text,
        'final_metrics': original_metrics,
        'final_enhanced_score': original_enhanced_score,
        'template_improvement': 0.0,
        'final_improvement': 0.0,
        'ollama_additional_improvement': 0.0
    }
    
    # Try template matching
    if question_type and question_type in PROMPT_TEMPLATES:
        templates = PROMPT_TEMPLATES[question_type]
        template, match_obj = match_question_to_template_simple(question_text, templates)
        
        if template and match_obj:
            template_improved_text = transform_question_with_template_simple(question_text, template, match_obj)
            template_metrics = calculate_metrics_for_text(template_improved_text)
            template_enhanced_score = sum([
                template_metrics['clarity'],
                template_metrics['conciseness'],
                template_metrics['technical_accuracy'],
                template_metrics['actionability']
            ]) / 4
            
            results.update({
                'template_matched': True,
                'template_improved_text': template_improved_text,
                'template_metrics': template_metrics,
                'template_enhanced_score': template_enhanced_score,
                'template_improvement': template_enhanced_score - original_enhanced_score
            })
    
    # Check if Ollama polishing is needed
    if not results['template_matched']:
        try:
            ollama_improved_text = polish_low_scoring_questions(
                results['template_improved_text'],
                results['template_metrics'],
                question_type or "Unknown"
            )
            
            if ollama_improved_text != results['template_improved_text']:
                final_metrics = calculate_metrics_for_text(ollama_improved_text)
                final_enhanced_score = sum([
                    final_metrics['clarity'],
                    final_metrics['conciseness'],
                    final_metrics['technical_accuracy'],
                    final_metrics['actionability']
                ]) / 4
                
                results.update({
                    'ollama_used': True,
                    'ollama_improved_text': ollama_improved_text,
                    'final_metrics': final_metrics,
                    'final_enhanced_score': final_enhanced_score,
                    'final_improvement': final_enhanced_score - original_enhanced_score,
                    'ollama_additional_improvement': final_enhanced_score - results['template_enhanced_score']
                })
            else:
                results['final_improvement'] = results['template_improvement']
        except Exception as e:
            # If Ollama fails, use template results
            results['final_improvement'] = results['template_improvement']
    elif should_polish_with_ollama(results['template_metrics'], threshold=9.0):
        try:
            ollama_improved_text = polish_low_scoring_questions(
                results['template_improved_text'],
                results['template_metrics'],
                question_type or "Unknown"
            )
            
            if ollama_improved_text != results['template_improved_text']:
                final_metrics = calculate_metrics_for_text(ollama_improved_text)
                final_enhanced_score = sum([
                    final_metrics['clarity'],
                    final_metrics['conciseness'],
                    final_metrics['technical_accuracy'],
                    final_metrics['actionability']
                ]) / 4
                
                results.update({
                    'ollama_used': True,
                    'ollama_improved_text': ollama_improved_text,
                    'final_metrics': final_metrics,
                    'final_enhanced_score': final_enhanced_score,
                    'final_improvement': final_enhanced_score - original_enhanced_score,
                    'ollama_additional_improvement': final_enhanced_score - results['template_enhanced_score']
                })
            else:
                results['final_improvement'] = results['template_improvement']
        except Exception as e:
            # If Ollama fails, use template results
            results['final_improvement'] = results['template_improvement']
    else:
        results['final_improvement'] = results['template_improvement']
    
    return results

if FLASK_AVAILABLE:
    @app.route('/')
    def index():
        """Home page with navigation."""
        return render_template('index.html')

    @app.route('/metrics')
    def metrics_page():
        """Page for analyzing any text and getting metrics."""
        return render_template('metrics.html')

    @app.route('/improve')
    def improve_page():
        """Page for improving questions with templates and Ollama."""
        question_types = get_question_types()
        return render_template('improve.html', question_types=question_types)

    @app.route('/templates')
    def templates_page():
        """Page for displaying all prompt templates."""
        # Calculate statistics in Python
        total_templates = sum(len(templates) for templates in PROMPT_TEMPLATES.values())
        max_templates_per_type = max(len(templates) for templates in PROMPT_TEMPLATES.values())
        avg_templates_per_type = total_templates / len(PROMPT_TEMPLATES) if PROMPT_TEMPLATES else 0
        
        stats = {
            'question_types': len(PROMPT_TEMPLATES),
            'total_templates': total_templates,
            'max_templates_per_type': max_templates_per_type,
            'avg_templates_per_type': round(avg_templates_per_type, 1)
        }
        
        return render_template('templates.html', prompt_templates=PROMPT_TEMPLATES, stats=stats)

    @app.route('/pipeline')
    def pipeline_page():
        """Page for displaying the pipeline diagram."""
        return render_template('pipeline.html')

    @app.route('/demo')
    def demo_page():
        """Page for demonstrating the pipeline with real examples from CSV."""
        return render_template('demo.html')

    @app.route('/api/calculate_metrics', methods=['POST'])
    def api_calculate_metrics():
        """API endpoint for calculating metrics for any text."""
        try:
            data = request.get_json()
            text = data.get('text', '').strip()
            
            if not text:
                return jsonify({'error': 'No text provided'}), 400
            
            metrics = calculate_metrics_for_text(text)
            enhanced_score = sum([
                metrics['clarity'],
                metrics['conciseness'],
                metrics['technical_accuracy'],
                metrics['actionability']
            ]) / 4
            
            return jsonify({
                'success': True,
                'text': text,
                'metrics': metrics,
                'enhanced_score': enhanced_score
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/improve_question', methods=['POST'])
    def api_improve_question():
        """API endpoint for improving questions through the pipeline."""
        try:
            data = request.get_json()
            question_text = data.get('question_text', '').strip()
            question_type = data.get('question_type', '').strip()
            
            if not question_text:
                return jsonify({'error': 'No question text provided'}), 400
            
            # Process through pipeline
            results = process_question_pipeline(question_text, question_type)
            
            return jsonify({
                'success': True,
                'results': results
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/start_ollama', methods=['POST'])
    def api_start_ollama():
        """API endpoint for manually triggering Ollama polishing."""
        try:
            data = request.get_json()
            question_text = data.get('question_text', '').strip()
            question_type = data.get('question_type', '').strip()
            
            if not question_text:
                return jsonify({'error': 'No question text provided'}), 400
            
            # Process through pipeline with Ollama
            results = process_question_pipeline(question_text, question_type)
            
            # Force Ollama polishing if not already used
            if not results['ollama_used']:
                try:
                    ollama_improved_text = polish_low_scoring_questions(
                        results['template_improved_text'],
                        results['template_metrics'],
                        question_type or "Unknown"
                    )
                    
                    if ollama_improved_text != results['template_improved_text']:
                        final_metrics = calculate_metrics_for_text(ollama_improved_text)
                        final_enhanced_score = sum([
                            final_metrics['clarity'],
                            final_metrics['conciseness'],
                            final_metrics['technical_accuracy'],
                            final_metrics['actionability']
                        ]) / 4
                        
                        results.update({
                            'ollama_used': True,
                            'ollama_improved_text': ollama_improved_text,
                            'final_metrics': final_metrics,
                            'final_enhanced_score': final_enhanced_score,
                            'final_improvement': final_enhanced_score - results['original_enhanced_score'],
                            'ollama_additional_improvement': final_enhanced_score - results['template_enhanced_score']
                        })
                except Exception as e:
                    results['error'] = f"Ollama polishing failed: {str(e)}"
            
            return jsonify({
                'success': True,
                'results': results
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/demo_examples', methods=['GET'])
    def api_demo_examples():
        """API endpoint for getting demo examples from CSV."""
        try:
            from simple_question_tester import get_demo_examples
            
            # Get 5 random examples for demo
            demo_examples = get_demo_examples(5)
            
            return jsonify({
                'success': True,
                'examples': demo_examples
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if not FLASK_AVAILABLE:
        print("❌ Flask is required to run the web application.")
        print("   Install with: pip install flask")
        exit(1)
    
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 Starting Question Improvement Web Application")
    print("=" * 60)
    print("📊 Available endpoints:")
    print("   • / - Home page")
    print("   • /metrics - Metrics analysis for any text")
    print("   • /improve - Question improvement with templates and Ollama")
    print("   • /templates - Browse all prompt templates")
    print("   • /pipeline - Pipeline diagram and workflow")
    print("   • /demo - Quick demo with real examples")
    print("   • /api/calculate_metrics - API for metrics calculation")
    print("   • /api/improve_question - API for question improvement")
    print("   • /api/start_ollama - API for manual Ollama polishing")
    print("   • /api/demo_examples - API for demo examples")
    print()
    print("🌐 Starting Flask development server...")
    print("   Open http://localhost:5000 in your browser")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5001) 