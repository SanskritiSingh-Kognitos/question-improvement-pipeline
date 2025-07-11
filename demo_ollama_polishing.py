#!/usr/bin/env python3
"""
Demo script for the Ollama polishing functionality.
Shows how questions with scores below 9.0 are automatically polished with Ollama.
"""

# Configuration
NUM_QUESTIONS = 5  # Change this to test with more or fewer questions

from simple_question_tester import (
    process_random_questions_with_ollama_polishing,
    should_polish_with_ollama,
    calculate_metrics_for_text
)

def demo_ollama_polishing():
    """Demonstrate Ollama polishing for low-scoring questions."""
    print("🤖 OLLAMA POLISHING DEMO")
    print("=" * 60)
    print(f"📊 Processing {NUM_QUESTIONS} questions with automatic Ollama polishing")
    print()
    
    # Process questions with Ollama polishing
    results = process_random_questions_with_ollama_polishing(NUM_QUESTIONS)
    
    if results:
        print("\n" + "="*60)
        print("📋 QUESTION-BY-QUESTION BREAKDOWN")
        print("="*60)
        
        for i, result in enumerate(results, 1):
            print(f"\n🔍 QUESTION {i}/{len(results)}")
            print("-" * 40)
            
            # Original question
            print(f"📝 ORIGINAL:")
            print(f"   {result['combined_text']}")
            print(f"   Type: {result['type']}")
            
            # Template improvement
            if result['template_matched']:
                print(f"\n✨ TEMPLATE IMPROVED:")
                print(f"   {result['template_improved_text']}")
                print(f"   Enhanced Score: {result['template_enhanced_score']:.3f}")
            else:
                print(f"\n❌ NO TEMPLATE MATCH")
                print(f"   Enhanced Score: {result['template_enhanced_score']:.3f}")
            
            # Ollama improvement
            if result['ollama_used']:
                print(f"\n🤖 OLLAMA IMPROVED:")
                print(f"   {result['ollama_improved_text']}")
                final_enhanced = sum([
                    result['final_metrics']['clarity'],
                    result['final_metrics']['conciseness'],
                    result['final_metrics']['technical_accuracy'],
                    result['final_metrics']['actionability']
                ]) / 4
                print(f"   Enhanced Score: {final_enhanced:.3f}")
            else:
                print(f"\n✅ NO OLLAMA NEEDED (score above 9.0)")
        
        # Final summary
        print("\n" + "="*60)
        print("📊 FINAL METRICS SUMMARY")
        print("="*60)
        
        # Calculate statistics
        total_questions = len(results)
        template_matched = sum(1 for r in results if r['template_matched'])
        ollama_used = sum(1 for r in results if r['ollama_used'])
        
        template_improvements = [r['template_improvement'] for r in results if r['template_matched']]
        ollama_improvements = [r['final_improvement'] for r in results if r['ollama_used']]
        
        print(f"📈 OVERALL STATISTICS:")
        print(f"   📊 Total questions processed: {total_questions}")
        print(f"   ✅ Template matches: {template_matched}/{total_questions}")
        print(f"   🤖 Ollama polishing used: {ollama_used}/{total_questions}")
        
        if template_improvements:
            avg_template_improvement = sum(template_improvements) / len(template_improvements)
            print(f"   📈 Average template improvement: {avg_template_improvement:+.3f}")
        
        if ollama_improvements:
            avg_ollama_improvement = sum(ollama_improvements) / len(ollama_improvements)
            print(f"   📈 Average final improvement: {avg_ollama_improvement:+.3f}")
        
        # Show question type distribution
        type_counts = {}
        for r in results:
            q_type = r['type']
            type_counts[q_type] = type_counts.get(q_type, 0) + 1
        
        print(f"\n📋 QUESTION TYPE DISTRIBUTION:")
        for q_type, count in type_counts.items():
            print(f"   {q_type}: {count}")

def demo_ollama_availability():
    """Check and demonstrate Ollama availability."""
    print(f"\n🔍 OLLAMA AVAILABILITY CHECK")
    print("=" * 60)
    
    try:
        from local_polisher import check_ollama_available, get_available_models
        
        if check_ollama_available():
            print("✅ Ollama is available!")
            models = get_available_models()
            if models:
                print(f"📋 Available models: {', '.join(models)}")
            else:
                print("⚠️  No models found. You may need to pull a model:")
                print("   ollama pull llama2")
        else:
            print("❌ Ollama is not available")
            print("   To enable Ollama polishing:")
            print("   1. Install Ollama from https://ollama.ai")
            print("   2. Start Ollama: ollama serve")
            print("   3. Pull a model: ollama pull llama2")
    except ImportError:
        print("❌ local_polisher module not available")
        print("   Make sure local_polisher.py is in the same directory")

if __name__ == "__main__":
    print("🚀 OLLAMA POLISHING DEMO")
    print("=" * 60)
    
    # Check Ollama availability first
    demo_ollama_availability()
    
    # Run the main Ollama polishing demo
    demo_ollama_polishing()