#!/usr/bin/env python3
"""
Demo script for the metrics comparison functionality.
Shows how to use the new metrics features to compare original vs improved text.
"""

# Configuration - Change this to adjust the number of questions processed
NUM_QUESTIONS = 50  # Change this value to process more or fewer questions

from simple_question_tester import (
    process_random_questions_with_metrics,
    process_all_questions_with_metrics,
    calculate_metrics_for_text,
    print_metrics_comparison
)

def demo_single_question():
    """Demonstrate metrics comparison for a single question."""
    print("🎯 DEMO: Single Question Metrics Comparison")
    print("=" * 60)
    
    # Process just one question with detailed metrics
    results = process_random_questions_with_metrics(1)
    
    if results:
        result = results[0]
        print(f"\n📊 SUMMARY:")
        print(f"   Question Type: {result['type']}")
        print(f"   Template Matched: {result['matched']}")
        if result['matched']:
            print(f"   Template Used: {result['matched_template']}")
            print(f"   Regex Groups: {result['regex_groups']}")

def demo_bulk_analysis():
    """Demonstrate bulk analysis with comprehensive statistics."""
    print(f"\n📊 DEMO: Bulk Analysis with Comprehensive Statistics ({NUM_QUESTIONS} questions)")
    print("=" * 60)
    
    # Process questions and show overall statistics
    stats = process_all_questions_with_metrics(sample_size=NUM_QUESTIONS)
    
    if stats:
        print(f"\n📈 KEY INSIGHTS:")
        print(f"   • {stats['match_rate']:.1f}% of questions matched templates")
        print(f"   • Average improvement: {stats['avg_improvement']:+.3f}")
        print(f"   • {stats['matched_count']}/{stats['total_processed']} questions improved")

def demo_large_sample():
    """Demonstrate processing a large sample of questions."""
    print(f"\n📊 DEMO: Large Sample Analysis ({NUM_QUESTIONS} Questions)")
    print("=" * 60)
    
    # Process random questions with detailed metrics
    results = process_random_questions_with_metrics(NUM_QUESTIONS)
    
    if results:
        matched = sum(1 for r in results if r['matched'])
        improvements = [r['improvement'] for r in results if r['matched']]
        
        if improvements:
            avg_improvement = sum(improvements) / len(improvements)
            max_improvement = max(improvements)
            min_improvement = min(improvements)
            positive_count = sum(1 for imp in improvements if imp > 0)
            
            print(f"\n📈 DETAILED STATISTICS:")
            print(f"   Total questions processed: {len(results)}")
            print(f"   Questions matched: {matched}")
            print(f"   Match rate: {matched/len(results)*100:.1f}%")
            print(f"   Average improvement: {avg_improvement:+.3f}")
            print(f"   Best improvement: {max_improvement:+.3f}")
            print(f"   Worst improvement: {min_improvement:+.3f}")
            print(f"   Questions with positive improvement: {positive_count}/{len(improvements)}")
            print(f"   Positive improvement rate: {positive_count/len(improvements)*100:.1f}%")
        
        # Show breakdown by question type
        type_stats = {}
        for result in results:
            q_type = result['type']
            if q_type not in type_stats:
                type_stats[q_type] = {'count': 0, 'matched': 0, 'improvements': []}
            
            type_stats[q_type]['count'] += 1
            if result['matched']:
                type_stats[q_type]['matched'] += 1
                type_stats[q_type]['improvements'].append(result['improvement'])
        
        print(f"\n📋 BREAKDOWN BY QUESTION TYPE:")
        for q_type, stats in type_stats.items():
            if stats['count'] > 0:
                match_rate = stats['matched'] / stats['count'] * 100
                print(f"   {q_type}:")
                print(f"      Count: {stats['count']}")
                print(f"      Matched: {stats['matched']} ({match_rate:.1f}%)")
                if stats['improvements']:
                    avg_imp = sum(stats['improvements']) / len(stats['improvements'])
                    print(f"      Avg improvement: {avg_imp:+.3f}")

def demo_custom_metrics():
    """Demonstrate custom metrics calculation."""
    print("\n🔧 DEMO: Custom Metrics Calculation")
    print("=" * 60)
    
    # Example texts to compare
    original_text = "Please provide api key"
    improved_text = "Provide the api key to authenticate with the system. This value is required to access the services and perform the requested operations."
    
    print("📝 Comparing custom texts:")
    print(f"   Original: {original_text}")
    print(f"   Improved: {improved_text}")
    
    # Calculate and display metrics
    print_metrics_comparison(original_text, improved_text, "Custom Example")

def overall_metrics_summary():
    """Generate an overall metrics summary combining all analyses."""
    print(f"\n🎯 OVERALL METRICS SUMMARY")
    print("=" * 60)
    print(f"📊 Processing {NUM_QUESTIONS} questions for comprehensive analysis...")
    
    # Get comprehensive statistics
    stats = process_all_questions_with_metrics(sample_size=NUM_QUESTIONS)
    
    if stats:
        print(f"\n📈 OVERALL PERFORMANCE METRICS:")
        print(f"   📊 Total Questions Processed: {stats['total_processed']}")
        print(f"   ✅ Template Matches: {stats['matched_count']}")
        print(f"   📈 Match Rate: {stats['match_rate']:.1f}%")
        print(f"   📊 Average Improvement: {stats['avg_improvement']:+.3f}")
        
        # Calculate additional statistics
        all_improvements = [r['improvement'] for r in stats['results'] if r['matched']]
        if all_improvements:
            max_imp = max(all_improvements)
            min_imp = min(all_improvements)
            positive_count = sum(1 for imp in all_improvements if imp > 0)
            std_dev = (sum((imp - stats['avg_improvement']) ** 2 for imp in all_improvements) / len(all_improvements)) ** 0.5
            
            print(f"   🏆 Best Improvement: {max_imp:+.3f}")
            print(f"   📉 Worst Improvement: {min_imp:+.3f}")
            print(f"   📊 Standard Deviation: {std_dev:.3f}")
            print(f"   ✅ Positive Improvements: {positive_count}/{len(all_improvements)}")
            print(f"   📈 Success Rate: {positive_count/len(all_improvements)*100:.1f}%")
        
        # Show improvements by question type
        print(f"\n📋 IMPROVEMENTS BY QUESTION TYPE:")
        for question_type, improvements in stats['improvements_by_type'].items():
            if improvements:
                type_avg = sum(improvements) / len(improvements)
                type_positive = sum(1 for imp in improvements if imp > 0)
                type_max = max(improvements)
                type_min = min(improvements)
                
                print(f"   {question_type}:")
                print(f"      Count: {len(improvements)}")
                print(f"      Avg Improvement: {type_avg:+.3f}")
                print(f"      Range: {type_min:+.3f} to {type_max:+.3f}")
                print(f"      Positive Rate: {type_positive/len(improvements)*100:.1f}%")
        
        # Performance assessment
        print(f"\n🎯 PERFORMANCE ASSESSMENT:")
        if stats['avg_improvement'] > 1.0:
            print(f"   🟢 EXCELLENT: Average improvement of {stats['avg_improvement']:+.3f} indicates strong template effectiveness")
        elif stats['avg_improvement'] > 0.5:
            print(f"   🟡 GOOD: Average improvement of {stats['avg_improvement']:+.3f} shows positive template impact")
        else:
            print(f"   🔴 NEEDS IMPROVEMENT: Average improvement of {stats['avg_improvement']:+.3f} suggests template optimization needed")
        
        if stats['match_rate'] > 90:
            print(f"   🟢 HIGH MATCH RATE: {stats['match_rate']:.1f}% of questions matched templates")
        elif stats['match_rate'] > 70:
            print(f"   🟡 MODERATE MATCH RATE: {stats['match_rate']:.1f}% of questions matched templates")
        else:
            print(f"   🔴 LOW MATCH RATE: {stats['match_rate']:.1f}% of questions matched templates - consider adding more templates")

if __name__ == "__main__":
    print("🚀 METRICS COMPARISON DEMO")
    print("=" * 60)
    print(f"📊 Configuration: Processing {NUM_QUESTIONS} questions")
    
    # Run all demos
    demo_single_question()
    demo_bulk_analysis()
    demo_large_sample()
    demo_custom_metrics()
    
    # Generate overall summary
    overall_metrics_summary()
    
    print("\n🎉 Demo completed!")
    print("\n💡 USAGE TIPS:")
    print("   • Change NUM_QUESTIONS at the top to adjust sample size")
    print("   • Use process_random_questions_with_metrics() for detailed analysis")
    print("   • Use process_all_questions_with_metrics() for bulk statistics")
    print("   • Use print_metrics_comparison() for custom text comparison")
    print("   • Use calculate_metrics_for_text() for individual metric calculation") 