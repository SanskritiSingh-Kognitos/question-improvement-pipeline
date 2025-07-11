#!/usr/bin/env python3
"""
Metrics Analyzer - Provides comprehensive metrics analysis for questions.
Shows original, template, and Ollama improvements with detailed statistics.
"""

# Configuration
NUM_QUESTIONS = 10000  # Change this to analyze more or fewer questions

from simple_question_tester import (
    process_random_questions_with_ollama_polishing,
    calculate_metrics_for_text,
    process_all_questions_with_metrics
)
import pandas as pd
from typing import Optional

def analyze_question_metrics(num_questions: int = 5):
    """Analyze metrics for a specified number of questions."""
    print("📊 METRICS ANALYZER")
    print("=" * 60)
    print(f"🔍 Analyzing {num_questions} questions for comprehensive metrics")
    print()
    
    # Process questions with full pipeline
    results = process_random_questions_with_ollama_polishing(num_questions)
    
    if not results:
        print("❌ No questions to analyze")
        return
    
    # Track statistics
    stats = {
        'total_questions': len(results),
        'template_matched': 0,
        'ollama_used': 0,
        'has_error_traceback': 0,
        'template_improvements': [],
        'ollama_improvements': [],
        'final_improvements': [],
        'question_types': {}
    }
    
    print("📋 QUESTION ANALYSIS")
    print("=" * 60)
    
    for i, result in enumerate(results, 1):
        print(f"\n🔍 QUESTION {i}/{len(results)}")
        print("-" * 50)
        
        # Question info
        print(f"📝 ORIGINAL: {result['combined_text']}")
        print(f"   Type: {result['type']}")
        
        # Track question type
        q_type = result['type']
        stats['question_types'][q_type] = stats['question_types'].get(q_type, 0) + 1
        
        # Check for error traceback
        if result.get('error_traceback') and str(result['error_traceback']).strip() != '':
            stats['has_error_traceback'] += 1
        
        # Template analysis
        if result['template_matched']:
            stats['template_matched'] += 1
            stats['template_improvements'].append(result['template_improvement'])
            print(f"✨ TEMPLATE: {result['template_improved_text']}")
            print(f"   Enhanced Score: {result['template_enhanced_score']:.3f}")
        else:
            print(f"❌ TEMPLATE: No match found")
            print(f"   Enhanced Score: {result['template_enhanced_score']:.3f}")
        
        # Ollama analysis
        if result['ollama_used']:
            stats['ollama_used'] += 1
            stats['ollama_improvements'].append(result['final_improvement'])
            print(f"🤖 OLLAMA: {result['ollama_improved_text']}")
            
            # Calculate final enhanced score
            final_metrics = result['final_metrics']
            final_enhanced = sum([
                final_metrics['clarity'],
                final_metrics['conciseness'],
                final_metrics['technical_accuracy'],
                final_metrics['actionability']
            ]) / 4
            print(f"   Enhanced Score: {final_enhanced:.3f}")
        else:
            print(f"✅ OLLAMA: Not needed (score above 9.0)")
        
        # Track final improvement
        stats['final_improvements'].append(result['final_improvement'])
        
        # Show individual metrics
        print(f"📊 METRICS:")
        original_metrics = result['original_metrics']
        print(f"   Original - Clarity: {original_metrics['clarity']:.3f}, Conciseness: {original_metrics['conciseness']:.3f}, Technical: {original_metrics['technical_accuracy']:.3f}, Actionability: {original_metrics['actionability']:.3f}")
        
        if result['template_matched']:
            template_metrics = result['template_metrics']
            print(f"   Template - Clarity: {template_metrics['clarity']:.3f}, Conciseness: {template_metrics['conciseness']:.3f}, Technical: {template_metrics['technical_accuracy']:.3f}, Actionability: {template_metrics['actionability']:.3f}")
        
        if result['ollama_used']:
            final_metrics = result['final_metrics']
            print(f"   Final   - Clarity: {final_metrics['clarity']:.3f}, Conciseness: {final_metrics['conciseness']:.3f}, Technical: {final_metrics['technical_accuracy']:.3f}, Actionability: {final_metrics['actionability']:.3f}")
    
    # Print comprehensive summary
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE METRICS SUMMARY")
    print("="*60)
    
    print(f"📈 OVERALL STATISTICS:")
    print(f"   📊 Total questions analyzed: {stats['total_questions']}")
    print(f"   ✅ Template matches: {stats['template_matched']}/{stats['total_questions']} ({stats['template_matched']/stats['total_questions']*100:.1f}%)")
    print(f"   🤖 Ollama polishing used: {stats['ollama_used']}/{stats['total_questions']} ({stats['ollama_used']/stats['total_questions']*100:.1f}%)")
    print(f"   🐛 Questions with error traceback: {stats['has_error_traceback']}/{stats['total_questions']} ({stats['has_error_traceback']/stats['total_questions']*100:.1f}%)")
    
    # Improvement statistics
    if stats['template_improvements']:
        avg_template_improvement = sum(stats['template_improvements']) / len(stats['template_improvements'])
        max_template_improvement = max(stats['template_improvements'])
        min_template_improvement = min(stats['template_improvements'])
        print(f"\n📈 TEMPLATE IMPROVEMENTS:")
        print(f"   📊 Average improvement: {avg_template_improvement:+.3f}")
        print(f"   📈 Best improvement: {max_template_improvement:+.3f}")
        print(f"   📉 Worst improvement: {min_template_improvement:+.3f}")
        print(f"   ✅ Positive improvements: {sum(1 for imp in stats['template_improvements'] if imp > 0)}/{len(stats['template_improvements'])}")
    
    if stats['ollama_improvements']:
        avg_ollama_improvement = sum(stats['ollama_improvements']) / len(stats['ollama_improvements'])
        max_ollama_improvement = max(stats['ollama_improvements'])
        min_ollama_improvement = min(stats['ollama_improvements'])
        print(f"\n🤖 OLLAMA IMPROVEMENTS:")
        print(f"   📊 Average improvement: {avg_ollama_improvement:+.3f}")
        print(f"   📈 Best improvement: {max_ollama_improvement:+.3f}")
        print(f"   📉 Worst improvement: {min_ollama_improvement:+.3f}")
        print(f"   ✅ Positive improvements: {sum(1 for imp in stats['ollama_improvements'] if imp > 0)}/{len(stats['ollama_improvements'])}")
    
    # Overall final improvements
    if stats['final_improvements']:
        avg_final_improvement = sum(stats['final_improvements']) / len(stats['final_improvements'])
        max_final_improvement = max(stats['final_improvements'])
        min_final_improvement = min(stats['final_improvements'])
        print(f"\n🎯 FINAL IMPROVEMENTS:")
        print(f"   📊 Average improvement: {avg_final_improvement:+.3f}")
        print(f"   📈 Best improvement: {max_final_improvement:+.3f}")
        print(f"   📉 Worst improvement: {min_final_improvement:+.3f}")
        print(f"   ✅ Positive improvements: {sum(1 for imp in stats['final_improvements'] if imp > 0)}/{len(stats['final_improvements'])}")
    
    # Question type distribution
    print(f"\n📋 QUESTION TYPE DISTRIBUTION:")
    for q_type, count in stats['question_types'].items():
        print(f"   {q_type}: {count} ({count/stats['total_questions']*100:.1f}%)")
    
    # Success rates
    print(f"\n🎯 SUCCESS RATES:")
    template_success_rate = stats['template_matched'] / stats['total_questions'] * 100
    ollama_success_rate = stats['ollama_used'] / stats['total_questions'] * 100
    positive_improvement_rate = sum(1 for imp in stats['final_improvements'] if imp > 0) / len(stats['final_improvements']) * 100
    
    print(f"   ✅ Template matching success: {template_success_rate:.1f}%")
    print(f"   🤖 Ollama polishing success: {ollama_success_rate:.1f}%")
    print(f"   📈 Positive improvement rate: {positive_improvement_rate:.1f}%")
    
    return stats

def analyze_all_questions(csv_file: str = "questions.csv", sample_size: Optional[int] = None):
    """
    Analyze all questions from the CSV file with comprehensive metrics.
    
    Args:
        csv_file: Path to the CSV file (default: "questions.csv")
        sample_size: Number of questions to sample (None = all questions)
    """
    print("🌍 COMPREHENSIVE ALL-QUESTIONS ANALYSIS")
    print("=" * 60)
    
    if sample_size is None:
        print("🔍 Analyzing ALL questions from the dataset")
    else:
        print(f"🔍 Analyzing {sample_size} questions from the dataset")
    print()
    
    try:
        # Read CSV to get total count
        df = pd.read_csv(csv_file)
        total_questions = len(df)
        print(f"📊 Total questions in dataset: {total_questions:,}")
        
        # Handle sample size
        if sample_size is None:
            sample_size = total_questions
        elif sample_size > total_questions:
            sample_size = total_questions
            print(f"⚠️  Sample size adjusted to {sample_size} (total available)")
        
        print(f"📋 Processing {sample_size:,} questions...")
        print("   (This may take a while for large datasets)")
        print()
        
        # Use the existing comprehensive analysis function
        stats = process_all_questions_with_metrics(csv_file, sample_size)
        
        if stats:
            print("\n" + "="*60)
            print("📊 COMPREHENSIVE ALL-QUESTIONS SUMMARY")
            print("="*60)
            
            print(f"📈 OVERALL STATISTICS:")
            print(f"   📊 Total questions processed: {stats['total_processed']:,}")
            print(f"   ✅ Template matches: {stats['matched_count']:,}/{stats['total_processed']:,} ({stats['match_rate']:.1f}%)")
            
            if stats.get('avg_improvement'):
                print(f"   📈 Average improvement: {stats['avg_improvement']:+.3f}")
            
            # Show improvements by question type
            if stats.get('improvements_by_type'):
                print(f"\n📋 IMPROVEMENTS BY QUESTION TYPE:")
                for question_type, improvements in stats['improvements_by_type'].items():
                    if improvements:
                        type_avg = sum(improvements) / len(improvements)
                        type_positive = sum(1 for imp in improvements if imp > 0)
                        print(f"   {question_type}:")
                        print(f"      Count: {len(improvements)}")
                        print(f"      Avg improvement: {type_avg:+.3f}")
                        print(f"      Positive rate: {type_positive/len(improvements)*100:.1f}%")
            
            print(f"\n🎉 Analysis completed successfully!")
            print(f"   📊 Processed {stats['total_processed']:,} questions")
            print(f"   ✅ Template match rate: {stats['match_rate']:.1f}%")
            
            if stats.get('avg_improvement'):
                print(f"   📈 Average improvement: {stats['avg_improvement']:+.3f}")
        
        return stats
        
    except FileNotFoundError:
        print(f"❌ Error: {csv_file} file not found")
        return None
    except Exception as e:
        print(f"❌ Error processing CSV: {e}")
        return None

def quick_metrics_test():
    """Run a quick test with a small number of questions."""
    print("🚀 QUICK METRICS TEST")
    print("=" * 60)
    
    # Test with 3 questions
    stats = analyze_question_metrics(3)
    
    if stats:
        print(f"\n✅ Quick test completed successfully!")
        print(f"   Processed {stats['total_questions']} questions")
        print(f"   Template matches: {stats['template_matched']}")
        print(f"   Ollama usage: {stats['ollama_used']}")

if __name__ == "__main__":
    print("🚀 METRICS ANALYZER")
    print("=" * 60)

    # analyze_all_questions()

    analyze_question_metrics(NUM_QUESTIONS)

    print(f"\n🎉 Analysis completed!")
    print(f"\n💡 USAGE TIPS:")
    print(f"   • Change NUM_QUESTIONS at the top to analyze more questions")
    print(f"   • Run 'python metrics_analyzer.py all' to analyze all questions")
    print(f"   • Questions are automatically processed through template matching and Ollama polishing")
    print(f"   • Metrics show clarity, conciseness, technical accuracy, and actionability")
    print(f"   • Enhanced scores below 9.0 trigger Ollama polishing") 