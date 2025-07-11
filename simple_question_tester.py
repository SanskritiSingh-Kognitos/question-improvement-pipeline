# simple_question_tester.py

import os
import re
import json
import pandas as pd
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Configuration
MAX_UNIQUE_QUESTIONS = 100
INTERACTIVE_MODE = False  # Set to False for automated mode

# Try to import Ollama for polishing, but make it optional
try:
    from local_polisher import polish_question_with_fallback, check_ollama_available, get_available_models

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Warning: Ollama polisher not available. Local polishing will be disabled.")
    polish_question_with_fallback = None

from metrics3 import (
    clarity,
    conciseness,
    technical_accuracy,
    actionability,
    compute_enhanced_scores
)


# Simple prompt templates
PROMPT_TEMPLATES = {
    # <FIELDEXPRESSION> is in form a|b|c... regex should capture this as c from b from a or
    # <FIELD> is in form a... regex should capture this as a
    # <NUMBER> is a number... regex should capture this as a number
    # <NUMBER2> is a number... regex should capture this as a number
    # <FIELD1> is in form a... regex should capture this as a
    # <FIELD2> is in form a... regex should capture this as a
    # <RUNS> is numerous lines of text... regex should capture this as a list of lines
    # <LINES> is numerous lines of text... regex should capture this in way specified under ParseErrorQuestion section
    # <EXPRESSION> is in MATH expression format... regex should capture this as a math expression

    "ValueNotKnownQuestion": [
        {
            # <FIELD> is in form a|b|c... regex should capture this in grammatically correct way
            "original": "Please provide <FIELDEXPRESSION>",
            "nicer": "Provide the <FIELDEXPRESSION> to authenticate with the system. This value is required to access the services and perform the requested operations."
        },
        {
            "original": "Select one of <FIELDEXPRESSION>",
            "nicer": "Select one of the available <FIELDEXPRESSION>. This selection will determine the scope of the processing operation."
        },
        {
            "original": "Multiple values found for table, please pick one",
            "nicer": "Multiple table options were found in the system. Select the specific value you want to work with from the available options to proceed with the operation."
        },
        {
            "original": "Automation run has taken <NUMBER> minutes.  Should it continue ?",
            "nicer": "The automation process has been running for <NUMBER> minutes. Decide whether to continue the operation or stop it based on your current requirements and system performance considerations."
        },
        {
            "original": "Please select a value to filter on.",
            "nicer": "Select a specific value from the available options to apply as a filter criterion. This selection will help narrow down the results to match your specific requirements."
        },
        {
            "original": "Multiple values found for <FIELD>, please pick one",
            "nicer": "Multiple values were found for the specified <FIELD>. Select the most appropriate value from the available options to proceed with the operation."
        },
        {
            "original": "Multiple values found for <FIELD>. Please select one.",
            "nicer": "Multiple values were found for the specified <FIELD>. Select the most appropriate value from the available options to proceed with the operation."
        },
        {
            "original": "The provided document has <NUMBER> pages; but we only support at max <NUMBER2> pages. Please re-upload a smaller document and rerun.",
            "nicer": "The uploaded document contains <NUMBER> pages, which exceeds the maximum supported limit of <NUMBER2> pages. Upload a smaller document that meets the size requirements and try again."
        },
        {
            "original": "I could not find invoice number for Pack Slip: <NUMBER>",
            "nicer": "Could not locate the invoice number for Pack Slip <NUMBER>. Verify the pack slip number exists in the system and ensure it has an associated invoice before proceeding."
        },
        {
            "original": "What database do you want to select?",
            "nicer": "Specify which database you would like to work with from the available options. This selection will determine the data source for the current operation."
        },
        {
            "original": "Which procedure should I use?",
            "nicer": "Select the appropriate procedure from the available options based on your specific requirements. This choice will determine the processing method for your operation."
        },
        {
            "original": "Multiple matches found, pick one",
            "nicer": "Multiple matching results were found. Select the most relevant option from the available matches to proceed with the operation."
        },
        {
            "original": "What do you want to do with the database?",
            "nicer": "Specify the operation you would like to perform on the database. This will determine the type of action to be executed on the selected data source."
        },
        {
            "original": "Unable to find the comparison column named <FIELD> in the table. Please choose the column name.",
            "nicer": "Could not locate the comparison column '<FIELD>' in the specified table. Select an existing column name from the available options to use for the comparison operation."
        },
        {
            "original": "I have found <NUMBER> possible matches for <FIELD> table. Please choose one.",
            "nicer": "Found <NUMBER> potential matches in the <FIELD> table. Select the most appropriate record from the available options to proceed with the operation."
        },
        {
            "original": "Un-loc code for <FIELD>",
            "nicer": "Please provide the UN/LOCODE for location <FIELD>. This standardized location code is required to identify the specific geographic location for the operation."
        },
        {
            "original": "Expected plural but got singular. Did you mean <FIELD>?",
            "nicer": "The system detected a singular form where a plural was expected. Did you mean \"<FIELD>\"? Please select the correct plural form to proceed with the operation."
        },
        {
            "original": "empty row <LINES>\nDo you want to add this almost-empty row to the table",
            "nicer": "Detected a row with mostly empty values: <LINES>\nWould you like to include this row in the table or exclude it from processing?"
        },
        {
            "original": "This record already exists\nHow would you like to proceed?",
            "nicer": "A record with the same identifier already exists in the system. How would you like to proceed with this duplicate entry?"
        },
        {
            "original": "The key <FIELD> does not exist\nHow would you like to proceed?",
            "nicer": "The specified key '<FIELD>' was not found in the system. How would you like to proceed with this missing reference?"
        },
        {
            "original": "The value <FIELD> for <FIELD2> exceeds allowed field length <NUMBER>\nDo you want to truncate the field?",
            "nicer": "The value '<FIELD>' for field '<FIELD2>' exceeds the maximum allowed length of <NUMBER> characters. Would you like to truncate the field to fit within the limit?"
        },
        {
            "original": "Folder <FIELD> does not exist. Create it ?",
            "nicer": "The specified folder '<FIELD>' does not exist in the system. Would you like to create this folder to proceed with the operation?"
        },
        {
            "original": "Please enter <FIELD>",
            "nicer": "Please provide the required <FIELD> to continue with the operation."
        },
        {
            "original": "Which mathematical action would you like to perform?",
            "nicer": "Select the mathematical operation you would like to perform on the data."
        },
        {
            "original": "yes or no",
            "nicer": "Please respond with 'yes' or 'no' to proceed with the operation."
        },
        {
            "original": "hello?",
            "nicer": "Hello! How can I assist you with your request?"
        },
        {
            "original": "The bucket where we will archive <FIELD>\nWhich bucket would you like?",
            "nicer": "Select the storage bucket where you would like to archive the <FIELD> data."
        },
        {
            "original": "what is the endpoint URL?",
            "nicer": "Please provide the endpoint URL for the API connection."
        },
        {
            "original": "The table already has a header\nHow would you like to proceed?",
            "nicer": "The table already contains header information. How would you like to proceed with the existing structure?"
        },
        {
            "original": "I could not determine whether the condition is true or not. Help me",
            "nicer": "The system could not evaluate the specified condition. Please provide additional information to help determine the correct outcome."
        },
        {
            "original": "Unknown separator <FIELD>. Please enter the seperator text.",
            "nicer": "The system encountered an unrecognized separator '<FIELD>'. Please specify the correct separator format to proceed."
        },
        {
            "original": "I got an invalid timezone. Which timezone would you like to use?",
            "nicer": "The specified timezone is not recognized. Please select a valid timezone from the available options."        },
        {
            "original": "Hmm, I might need some more guidance. Tell me how to look for it.",
            "nicer": "I need additional guidance to locate the requested information. Please provide more specific instructions on how to proceed."
        },
        {
            "original": "This value is invalid\nHow would you like to proceed?",
            "nicer": "The provided value does not meet the required format or validation criteria. How would you like to proceed with this invalid entry?"
        },
        {
            "original": "Do you mean \"<FIELD>\" from \"<FIELD2>\" above or is this new?",
            "nicer": "Please clarify if you are referring to the existing '<FIELD>' from '<FIELD2>' or if this is a new reference."
        },
        {
            "original": "which fruit you like most?",
            "nicer": "Please select your preferred fruit from the available options."
        },
        {
            "original": "Enter the operator (+, -, *, /):",
            "nicer": "Please specify the mathematical operator (+, -, *, /) to use for the calculation."
        },
        {
            "original": "This key does not exist\nHow would you like to proceed?",
            "nicer": "The specified key was not found in the system. How would you like to proceed with this missing reference?"
        },
        {
            "original": "Enter the <FIELD> number:",
            "nicer":"Please provide the <FIELD> number for the calculation."
        },
        {
            "original": "Please enter the full name (first name and last name):",
            "nicer": "Please provide your complete name including both first and last name."
        },
        {
            "original": "A-GC99999-1",
            "nicer": "Please provide the required identifier or reference number. (A-GC99999-1)"
        },
        {
            "original": "oops",
            "nicer": "An error occurred. Please provide more information about what you were trying to do."
        }
    ],

    # always use ollama for this
    "NativeCodeErrorQuestion": [

    ],

    "ParseErrorQuestion": [
        # regex should capture how many lines they are
        # for each line it should do this
        # `ensure the data's Gross Weight is not negative` -> `ensure the data's Gross Weight is not negative` : Replace "ensure" with "validate" or "check"
        # same line + " : Replace "ensure" with "validate" or "check"
        # `send ""success""` : the line must have an ensure clause against a defined fact -> send "success"` : Add an ensure clause to validate against a defined fact before sending the success message.
        # perfrom tests on this or use ollama
        {
            "original": "Please resolve the following lines, and run again <LINES>",
            "nicer": "Please resolve the following validation errors and run again: <LINES>"
        },
    ],

    "EnsureFailedQuestion": [
        {
            "original": "Could not ensure that the <FIELD> is not \"<NUMBER>\".",
            "nicer": "Could not validate that the <FIELD> value is not <NUMBER>. Check the data source and ensure proper validation is in place before proceeding."
        },
        {
            "original": "Could not ensure that the <FIELD1> and <FIELD2> is not \"<NUMBER>\".",
            "nicer": "Could not validate that the <FIELD1> and <FIELD2> are not \"<NUMBER>\". Check data source and implement validation."
        },
        {
            "original": "Could not ensure that the <FIELD> is before the <FIELD2>.",
            "nicer": "Could not validate that the <FIELD> is chronologically before the <FIELD2>. Verify the date sequence and implement proper date validation with error handling before proceeding."
        },
        {
            "original": "Could not ensure that <EXPRESSION> is numeric.",
            "nicer": "Could not validate that the parsed expression \"the lineamt\" is numeric. The system detected a formatted string with determiner parsing that failed numeric validation. Please verify the data format and ensure the field contains only valid numbers before proceeding."
        },
        {
            "original": "Could not ensure that the <FIELD>'s columns are unique.",
            "nicer": "Check for duplicate column names in <FIELD> and ensure each column has a distinct identifier before proceeding with the operation."
        },
        {
            "original": "Could not ensure that the <FIELD>'s length is <NUMBER>.",
            "nicer": "Verify the <FIELD> format and ensure it contains exactly <NUMBER> characters before proceeding."
        },
        {
            "original": "Could not ensure that the <FIELD>'s characters is numeric.",
            "nicer": "Verify the <FIELD>'s format and ensure it contains only digits (0-9) before proceeding."
        },
        {
            "original": "Could not ensure that the <FIELD>'s weight is <EXPRESSION>.",
            "nicer": "Could not validate that the <FIELD> meets the required mathematical criteria. Verify the <FIELD> calculation and ensure it satisfies the specified formula, <EXPRESSION>, before proceeding."
        },
        {
            "original": "Could not ensure that the <FIELD> > <NUMBER>.",
            "nicer": "Could not validate that the <FIELD> is greater than <NUMBER>. Verify the score calculation and ensure it exceeds the minimum threshold of 40 before proceeding."
        },
        {
            "original": "Could not ensure that <EXPRESSION>.",
            "nicer": "Could not validate that the <EXPRESSION>. Verify the score calculation and ensure it matches the expression before proceeding."
        }
    ],

    "FactsValidationQuestion": [
        {
            "original": "Please review the following facts.",
            "nicer": "Confirm all the following information is correct and verify system configuration settings before proceeding with the operation. Validate data integrity and ensure all required parameters are properly configured."
        }
    ],

    "ReviewConceptQuestion": [
        {
            "original": "Please review <FIELDEXPRESSION>",
            "nicer": "Check the <FIELDEXPRESSION> and ensure it is correct."
        }
    ]
}

def _fieldepression_to_english(expr: str) -> str:
    """Convert a|b|c to 'c from b from a', a|b to 'b from a', a to 'a'"""
    parts = expr.split('|')
    if len(parts) == 1:
        return parts[0]
    else:
        return ' from '.join(reversed(parts))

def create_flexible_regex_pattern(template: str) -> str:
    """
    Create a flexible regex pattern that matches templates with placeholders.
    Uses loose matching to handle minor variations in text, spaces, and newlines.
    """
    # Normalize multiple spaces to single spaces in template
    pattern = re.sub(r'\s+', ' ', template)
    
    # Make <RUNS> extra flexible for whitespace after colon and before 'Come back here and retry'
    pattern = pattern.replace(":<RUNS>Come back here and retry", r":([\s\S]+?)Come back here and retry")
    # The rest as before
    pattern = pattern.replace("<FIELDEXPRESSION>", r"([\s\S]+?)")
    pattern = pattern.replace("<FIELD>", r"([\s\S]+?)")
    pattern = pattern.replace("<FIELD1>", r"([\s\S]+?)")
    pattern = pattern.replace("<FIELD2>", r"([\s\S]+?)")
    pattern = pattern.replace("<NUMBER>", r"(\d+(?:\.\d+)?)")
    pattern = pattern.replace("<NUMBER2>", r"(\d+(?:\.\d+)?)")
    pattern = pattern.replace("<LINES>", r"([\s\S]+)")
    pattern = pattern.replace("<EXPRESSION>", r"([\s\S]+?)")
    pattern = pattern.replace("<WORKER_ID>", r"([\s\S]+?)")
    # Escape regex special characters except for our capture groups
    placeholder_map = {
        r"([\s\S]+?)": "___CAPTURE___",
        r"(\d+(?:\.\d+)?)": "___NUMBER___",
        r"([\s\S]+)": "___LINES___"
    }
    for regex, token in placeholder_map.items():
        pattern = pattern.replace(regex, token)
    pattern = re.escape(pattern)
    pattern = pattern.replace("___CAPTURE___", r"([\s\S]+?)")
    pattern = pattern.replace("___NUMBER___", r"(\d+(?:\.\d+)?)")
    pattern = pattern.replace("___LINES___", r"([\s\S]+)")
    # Replace all literal spaces with \s+ to allow for any whitespace
    pattern = pattern.replace(r"\ ", r"\s+")
    # Simple: allow optional punctuation at the end
    pattern = pattern.rstrip() + r"(?:[.!?,;:\-]*)?"
    pattern = r"^\s*" + pattern.strip() + r"\s*$"
    return pattern

def match_question_to_template_simple(question_text: str, templates: List[Dict]) -> Tuple[Optional[Dict], Optional[re.Match]]:
    """
    Simple template matching using flexible regex.
    Returns the best matching template and regex match object.
    """
    best_match = None
    best_match_obj = None
    
    for template in templates:
        original = template["original"]
        
        # Create flexible regex pattern
        pattern = create_flexible_regex_pattern(original)
        
        # Try to match with case insensitive and dotall flags
        match = re.match(pattern, question_text, re.IGNORECASE | re.DOTALL)
        
        if match:
            # Found a match - return it
            return template, match
    
    # No regex match found
    return None, None

def transform_question_with_template_simple(question_text: str, template: Dict, match_obj: re.Match) -> str:
    """
    Transform question using template and captured groups.
    Handles the specific placeholder requirements.
    """
    nicer_text = template["nicer"]
    
    if match_obj:
        groups = match_obj.groups()
        group_index = 0
        
        # Handle <FIELDEXPRESSION> - convert a|b|c to "c from b from a"
        if '<FIELDEXPRESSION>' in nicer_text and group_index < len(groups):
            field_expr = groups[group_index]
            field_expr_english = _fieldepression_to_english(field_expr)
            nicer_text = nicer_text.replace('<FIELDEXPRESSION>', field_expr_english)
            group_index += 1
        
        # Handle <FIELD>
        if '<FIELD>' in nicer_text and group_index < len(groups):
            field = groups[group_index]
            nicer_text = nicer_text.replace('<FIELD>', field)
            group_index += 1
        
        # Handle <FIELD1> and <FIELD2>
        if '<FIELD1>' in nicer_text and group_index < len(groups):
            field1 = groups[group_index]
            nicer_text = nicer_text.replace('<FIELD1>', field1)
            group_index += 1
        
        if '<FIELD2>' in nicer_text and group_index < len(groups):
            field2 = groups[group_index]
            nicer_text = nicer_text.replace('<FIELD2>', field2)
            group_index += 1
        
        # Handle <NUMBER> and <NUMBER2>
        if '<NUMBER>' in nicer_text and group_index < len(groups):
            number = groups[group_index]
            nicer_text = nicer_text.replace('<NUMBER>', number)
            group_index += 1
        
        if '<NUMBER2>' in nicer_text and group_index < len(groups):
            number2 = groups[group_index]
            nicer_text = nicer_text.replace('<NUMBER2>', number2)
            group_index += 1
        
        # Handle <RUNS> and <LINES>
        if '<RUNS>' in nicer_text and group_index < len(groups):
            runs = groups[group_index]
            nicer_text = nicer_text.replace('<RUNS>', runs)
            group_index += 1
        
        if '<LINES>' in nicer_text and group_index < len(groups):
            lines = groups[group_index]
            nicer_text = nicer_text.replace('<LINES>', lines)
            group_index += 1
        
        # Handle <EXPRESSION>
        if '<EXPRESSION>' in nicer_text and group_index < len(groups):
            expression = groups[group_index]
            nicer_text = nicer_text.replace('<EXPRESSION>', expression)
            group_index += 1
        
        # Handle <WORKER_ID>
        if '<WORKER_ID>' in nicer_text and group_index < len(groups):
            worker_id = groups[group_index]
            nicer_text = nicer_text.replace('<WORKER_ID>', worker_id)
            group_index += 1
    
    return nicer_text

def get_random_questions_from_csv(num_questions: int = 10, csv_file: str = "questions.csv") -> List[Dict]:
    """
    Get a specified number of random unique questions from questions.csv with diversity.
    
    Args:
        num_questions: Number of random questions to return (default: 10)
        csv_file: Path to the CSV file (default: "questions.csv")
    
    Returns:
        List of dictionaries containing question data with keys:
        - id: Question ID
        - text: Question text
        - lexical_path: Lexical path (if any)
        - type: Question type
        - error_traceback: Error traceback (if any)
        - choices: Choices (if any)
        - combined_text: text + lexical_path combined
    """
    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        print(f"📊 Loaded {len(df)} questions from {csv_file}")
        
        # Ensure we get diverse question types
        question_types = df['type'].value_counts()
        print(f"📋 Available question types: {list(question_types.index)}")
        
        # Calculate how many questions to sample from each type
        # Prioritize less common types to ensure diversity
        total_questions = len(df)
        questions = []
        
        # First, try to get at least one question from each available type
        available_types = df['type'].unique()
        type_questions = {}
        
        for q_type in available_types:
            type_df = df[df['type'] == q_type]
            if len(type_df) > 0:
                # Sample 1-2 questions from each type to ensure diversity
                sample_size = min(2, len(type_df))
                sampled = type_df.sample(n=sample_size, random_state=42)
                type_questions[q_type] = sampled
        
        # If we have enough diverse questions, use them
        total_diverse = sum(len(sampled) for sampled in type_questions.values())
        
        if total_diverse >= num_questions:
            # Use diverse sampling
            all_sampled = []
            for q_type, sampled_df in type_questions.items():
                all_sampled.append(sampled_df)
            
            combined_df = pd.concat(all_sampled, ignore_index=True)
            # Sample from the diverse set
            if len(combined_df) > num_questions:
                final_sampled = combined_df.sample(n=num_questions, random_state=42)
            else:
                final_sampled = combined_df
        else:
            # Fall back to regular random sampling but with more variety
            # Sample from different parts of the dataset
            chunk_size = len(df) // 4
            chunks = []
            for i in range(4):
                start_idx = i * chunk_size
                end_idx = start_idx + chunk_size if i < 3 else len(df)
                chunk = df.iloc[start_idx:end_idx]
                chunks.append(chunk)
            
            # Sample from each chunk to ensure variety
            samples_per_chunk = max(1, num_questions // 4)
            sampled_chunks = []
            for chunk in chunks:
                if len(chunk) > 0:
                    chunk_sample = chunk.sample(n=min(samples_per_chunk, len(chunk)), random_state=42)
                    sampled_chunks.append(chunk_sample)
            
            combined_df = pd.concat(sampled_chunks, ignore_index=True)
            if len(combined_df) > num_questions:
                final_sampled = combined_df.sample(n=num_questions, random_state=42)
            else:
                final_sampled = combined_df
        
        # Process the sampled questions
        for idx, row in final_sampled.iterrows():
            # Combine text + lexical_path as requested
            text = str(row['text']).strip()
            lexical_path = str(row.get('lexical_path', '')).strip()
            
            # Filter out nan values
            if lexical_path == 'nan' or lexical_path == '':
                combined_text = text
            else:
                combined_text = text + " " + lexical_path
            
            combined_text = combined_text.strip()
            
            if not combined_text or combined_text == 'nan':
                continue
            
            question_data = {
                'id': row.get('id', idx),
                'text': text,
                'lexical_path': lexical_path,
                'type': row.get('type', ''),
                'error_traceback': row.get('error_traceback', ''),
                'choices': row.get('choices', ''),
                'combined_text': combined_text
            }
            questions.append(question_data)
        
        # If we still don't have enough questions, add some random ones
        if len(questions) < num_questions:
            remaining_needed = num_questions - len(questions)
            remaining_df = df[~df.index.isin(final_sampled.index)]
            if len(remaining_df) > 0:
                additional_sampled = remaining_df.sample(n=min(remaining_needed, len(remaining_df)), random_state=42)
                for idx, row in additional_sampled.iterrows():
                    text = str(row['text']).strip()
                    lexical_path = str(row.get('lexical_path', '')).strip()
                    
                    if lexical_path == 'nan' or lexical_path == '':
                        combined_text = text
                    else:
                        combined_text = text + " " + lexical_path
                    
                    combined_text = combined_text.strip()
                    
                    if not combined_text or combined_text == 'nan':
                        continue
                    
                    question_data = {
                        'id': row.get('id', idx),
                        'text': text,
                        'lexical_path': lexical_path,
                        'type': row.get('type', ''),
                        'error_traceback': row.get('error_traceback', ''),
                        'choices': row.get('choices', ''),
                        'combined_text': combined_text
                    }
                    questions.append(question_data)
        
        # Show diversity summary
        type_counts = {}
        for q in questions:
            q_type = q['type']
            type_counts[q_type] = type_counts.get(q_type, 0) + 1
        
        print(f"✅ Retrieved {len(questions)} diverse questions")
        print(f"📊 Question type distribution:")
        for q_type, count in type_counts.items():
            print(f"   {q_type}: {count}")
        
        return questions
        
    except FileNotFoundError:
        print(f"❌ Error: {csv_file} file not found in current directory")
        return []
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return []

def get_demo_examples(num_examples: int = 5, csv_file: str = "questions.csv") -> List[Dict]:
    """
    Get demo examples from CSV and process them through the pipeline.
    
    Args:
        num_examples: Number of demo examples to return (default: 5)
        csv_file: Path to the CSV file (default: "questions.csv")
    
    Returns:
        List of dictionaries containing processed demo examples
    """
    questions = get_random_questions_from_csv(num_examples, csv_file)
    demo_examples = []
    
    for question_data in questions:
        question_text = question_data['combined_text']
        question_type = question_data['type']
        
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
        
        # Check if Ollama polishing is needed - FIRST check if no template matched
        if not results['template_matched']:
            print(f"   🔧 No template matched - forcing Ollama polishing")
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
        # SECOND check if template matched but score is low
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
        
        demo_example = {
            'original': {
                'text': question_data['text'],
                'lexical_path': question_data['lexical_path'],
                'type': question_type,
                'combined_text': question_data['combined_text']
            },
            'pipeline_results': results
        }
        
        demo_examples.append(demo_example)
    
    return demo_examples

def process_random_questions(num_questions: int = 10, csv_file: str = "questions.csv") -> List[Dict]:
    """
    Process a specified number of random questions with template matching.
    
    Args:
        num_questions: Number of random questions to process (default: 10)
        csv_file: Path to the CSV file (default: "questions.csv")
    
    Returns:
        List of dictionaries containing processed question data with template matching results
    """
    questions = get_random_questions_from_csv(num_questions, csv_file)
    results = []
    
    for question_data in questions:
        question_text = question_data['combined_text']
        question_type = question_data['type']
        
        print(f"\n📝 Processing: {question_text[:80]}{'...' if len(question_text) > 80 else ''}")
        print(f"   Type: {question_type}")
        
        if question_type in PROMPT_TEMPLATES:
            templates = PROMPT_TEMPLATES[question_type]
            template, match_obj = match_question_to_template_simple(question_text, templates)
            
            if template and match_obj:
                nicer_text = transform_question_with_template_simple(question_text, template, match_obj)
                print(f"   ✅ Matched template: {template['original']}")
                print(f"   ✨ Improved: {nicer_text[:80]}{'...' if len(nicer_text) > 80 else ''}")
                print(f"   🔍 Regex groups: {match_obj.groups()}")
                
                result = {
                    **question_data,
                    'matched_template': template['original'],
                    'nicer_text': nicer_text,
                    'regex_groups': match_obj.groups(),
                    'matched': True
                }
            else:
                print(f"   ❌ No template match found")
                result = {
                    **question_data,
                    'matched_template': None,
                    'nicer_text': question_text,
                    'regex_groups': None,
                    'matched': False
                }
        else:
            print(f"   ⚠️ No templates for type: {question_type}")
            result = {
                **question_data,
                'matched_template': None,
                'nicer_text': question_text,
                'regex_groups': None,
                'matched': False
            }
        
        results.append(result)
    
    return results


def test_random_questions():
    """Test the random question functions."""
    print("\n🎲 Testing Random Question Functions")
    print("=" * 50)
    
    # Test getting 5 random questions
    print("\n📋 Getting 5 random questions:")
    questions = get_random_questions_from_csv(5)
    
    for i, q in enumerate(questions, 1):
        print(f"   {i}. [{q['type']}] {q['combined_text'][:60]}{'...' if len(q['combined_text']) > 60 else ''}")
    
    # Test processing 3 random questions
    print("\n🔧 Processing 3 random questions with template matching:")
    results = process_random_questions(3)
    
    print(f"\n📊 Summary:")
    matched = sum(1 for r in results if r['matched'])
    print(f"   ✅ Matched: {matched}")
    print(f"   ❌ Unmatched: {len(results) - matched}")
    print(f"   📈 Success rate: {matched/len(results)*100:.1f}%")

def test_metrics_comparison():
    """Test the metrics comparison functionality."""
    print("\n📊 Testing Metrics Comparison")
    print("=" * 50)
    
    # Process 2 random questions with metrics
    results = process_random_questions_with_metrics(2)
    
    # Calculate overall improvements
    total_improvements = []
    for result in results:
        if result['matched']:
            original_avg = (result['original_metrics']['clarity'] + 
                          result['original_metrics']['conciseness'] + 
                          result['original_metrics']['technical_accuracy'] + 
                          result['original_metrics']['actionability']) / 4
            improved_avg = (result['improved_metrics']['clarity'] + 
                          result['improved_metrics']['conciseness'] + 
                          result['improved_metrics']['technical_accuracy'] + 
                          result['improved_metrics']['actionability']) / 4
            improvement = improved_avg - original_avg
            total_improvements.append(improvement)
    
    if total_improvements:
        avg_improvement = sum(total_improvements) / len(total_improvements)
        print(f"\n📈 OVERALL METRICS SUMMARY:")
        print(f"   Average improvement per question: {avg_improvement:+.3f}")
        print(f"   Questions with improvements: {len(total_improvements)}")
        print(f"   Questions processed: {len(results)}")

def calculate_metrics_for_text(text: str) -> Dict[str, float]:
    """
    Calculate metrics for a given text.
    
    Args:
        text: The text to evaluate
        
    Returns:
        Dictionary with metric scores
    """
    try:
        # Calculate individual metrics
        clarity_score = clarity(text)
        conciseness_score = conciseness(text)
        technical_accuracy_score = technical_accuracy(text)
        actionability_score = actionability(text)
        
        # Calculate enhanced scores using individual functions
        # Note: These functions might need to be imported or defined differently
        # For now, we'll use the basic scores as enhanced scores
        enhanced_clarity = clarity_score
        enhanced_conciseness = conciseness_score
        enhanced_technical_accuracy = technical_accuracy_score
        enhanced_actionability = actionability_score
        
        return {
            'clarity': clarity_score,
            'conciseness': conciseness_score,
            'technical_accuracy': technical_accuracy_score,
            'actionability': actionability_score,
            'enhanced_clarity': enhanced_clarity,
            'enhanced_conciseness': enhanced_conciseness,
            'enhanced_technical_accuracy': enhanced_technical_accuracy,
            'enhanced_actionability': enhanced_actionability
        }
    except Exception as e:
        print(f"⚠️  Error calculating metrics: {e}")
        return {
            'clarity': 0.0,
            'conciseness': 0.0,
            'technical_accuracy': 0.0,
            'actionability': 0.0,
            'enhanced_clarity': 0.0,
            'enhanced_conciseness': 0.0,
            'enhanced_technical_accuracy': 0.0,
            'enhanced_actionability': 0.0
        }

def print_metrics_comparison(original_text: str, improved_text: str, question_type: str = ""):
    """
    Print a comparison of metrics between original and improved text.
    
    Args:
        original_text: The original question text
        improved_text: The template-improved text
        question_type: The type of question (optional)
    """
    print(f"\n📊 METRICS COMPARISON {f'({question_type})' if question_type else ''}")
    print("=" * 60)
    
    # Calculate metrics for both texts
    original_metrics = calculate_metrics_for_text(original_text)
    improved_metrics = calculate_metrics_for_text(improved_text)
    
    # Print original text and metrics
    print(f"📝 ORIGINAL TEXT:")
    print(f"   {original_text}")
    print(f"   📈 Metrics:")
    print(f"      Clarity: {original_metrics['clarity']:.3f}")
    print(f"      Conciseness: {original_metrics['conciseness']:.3f}")
    print(f"      Technical Accuracy: {original_metrics['technical_accuracy']:.3f}")
    print(f"      Actionability: {original_metrics['actionability']:.3f}")
    print(f"      Enhanced Clarity: {original_metrics['enhanced_clarity']:.3f}")
    print(f"      Enhanced Conciseness: {original_metrics['enhanced_conciseness']:.3f}")
    print(f"      Enhanced Technical Accuracy: {original_metrics['enhanced_technical_accuracy']:.3f}")
    print(f"      Enhanced Actionability: {original_metrics['enhanced_actionability']:.3f}")
    
    # Print improved text and metrics
    print(f"\n✨ TEMPLATE-IMPROVED TEXT:")
    print(f"   {improved_text}")
    print(f"   📈 Metrics:")
    print(f"      Clarity: {improved_metrics['clarity']:.3f}")
    print(f"      Conciseness: {improved_metrics['conciseness']:.3f}")
    print(f"      Technical Accuracy: {improved_metrics['technical_accuracy']:.3f}")
    print(f"      Actionability: {improved_metrics['actionability']:.3f}")
    print(f"      Enhanced Clarity: {improved_metrics['enhanced_clarity']:.3f}")
    print(f"      Enhanced Conciseness: {improved_metrics['enhanced_conciseness']:.3f}")
    print(f"      Enhanced Technical Accuracy: {improved_metrics['enhanced_technical_accuracy']:.3f}")
    print(f"      Enhanced Actionability: {improved_metrics['enhanced_actionability']:.3f}")
    
    # Calculate improvements
    print(f"\n📈 IMPROVEMENTS:")
    clarity_improvement = improved_metrics['clarity'] - original_metrics['clarity']
    conciseness_improvement = improved_metrics['conciseness'] - original_metrics['conciseness']
    technical_improvement = improved_metrics['technical_accuracy'] - original_metrics['technical_accuracy']
    actionability_improvement = improved_metrics['actionability'] - original_metrics['actionability']
    
    print(f"      Clarity: {clarity_improvement:+.3f}")
    print(f"      Conciseness: {conciseness_improvement:+.3f}")
    print(f"      Technical Accuracy: {technical_improvement:+.3f}")
    print(f"      Actionability: {actionability_improvement:+.3f}")
    
    # Calculate overall improvement
    original_avg = (original_metrics['clarity'] + original_metrics['conciseness'] + 
                   original_metrics['technical_accuracy'] + original_metrics['actionability']) / 4
    improved_avg = (improved_metrics['clarity'] + improved_metrics['conciseness'] + 
                   improved_metrics['technical_accuracy'] + improved_metrics['actionability']) / 4
    overall_improvement = improved_avg - original_avg
    
    print(f"      Overall Average: {overall_improvement:+.3f}")

def process_random_questions_with_metrics(num_questions: int = 10, csv_file: str = "questions.csv") -> List[Dict]:
    """
    Process a specified number of random questions with template matching and metrics comparison.
    
    Args:
        num_questions: Number of random questions to process (default: 10)
        csv_file: Path to the CSV file (default: "questions.csv")
    
    Returns:
        List of dictionaries containing processed question data with template matching results and metrics
    """
    questions = get_random_questions_from_csv(num_questions, csv_file)
    results = []
    
    for i, question_data in enumerate(questions, 1):
        question_text = question_data['combined_text']
        question_type = question_data['type']
        
        print(f"\n{'='*60}")
        print(f"📝 QUESTION {i}/{len(questions)}: {question_text[:80]}{'...' if len(question_text) > 80 else ''}")
        print(f"   Type: {question_type}")
        
        if question_type in PROMPT_TEMPLATES:
            templates = PROMPT_TEMPLATES[question_type]
            template, match_obj = match_question_to_template_simple(question_text, templates)
            
            if template and match_obj:
                nicer_text = transform_question_with_template_simple(question_text, template, match_obj)
                print(f"   ✅ Matched template: {template['original']}")
                print(f"   🔍 Regex groups: {match_obj.groups()}")
                
                # Calculate and display metrics comparison
                print_metrics_comparison(question_text, nicer_text, question_type)
                
                # Calculate improvement
                original_metrics = calculate_metrics_for_text(question_text)
                improved_metrics = calculate_metrics_for_text(nicer_text)
                original_avg = (original_metrics['clarity'] + original_metrics['conciseness'] + 
                              original_metrics['technical_accuracy'] + original_metrics['actionability']) / 4
                improved_avg = (improved_metrics['clarity'] + improved_metrics['conciseness'] + 
                              improved_metrics['technical_accuracy'] + improved_metrics['actionability']) / 4
                improvement = improved_avg - original_avg
                
                result = {
                    **question_data,
                    'matched_template': template['original'],
                    'nicer_text': nicer_text,
                    'regex_groups': match_obj.groups(),
                    'matched': True,
                    'original_metrics': original_metrics,
                    'improved_metrics': improved_metrics,
                    'improvement': improvement
                }
            else:
                print(f"   ❌ No template match found")
                print(f"   📊 Metrics for original text only:")
                original_metrics = calculate_metrics_for_text(question_text)
                print(f"      Clarity: {original_metrics['clarity']:.3f}")
                print(f"      Conciseness: {original_metrics['conciseness']:.3f}")
                print(f"      Technical Accuracy: {original_metrics['technical_accuracy']:.3f}")
                print(f"      Actionability: {original_metrics['actionability']:.3f}")
                
                result = {
                    **question_data,
                    'matched_template': None,
                    'nicer_text': question_text,
                    'regex_groups': None,
                    'matched': False,
                    'original_metrics': original_metrics,
                    'improved_metrics': original_metrics,  # Same as original since no improvement
                    'improvement': 0.0  # No improvement
                }
        else:
            print(f"   ⚠️  No templates for type: {question_type}")
            print(f"   📊 Metrics for original text only:")
            original_metrics = calculate_metrics_for_text(question_text)
            print(f"      Clarity: {original_metrics['clarity']:.3f}")
            print(f"      Conciseness: {original_metrics['conciseness']:.3f}")
            print(f"      Technical Accuracy: {original_metrics['technical_accuracy']:.3f}")
            print(f"      Actionability: {original_metrics['actionability']:.3f}")
            
            result = {
                **question_data,
                'matched_template': None,
                'nicer_text': question_text,
                'regex_groups': None,
                'matched': False,
                'original_metrics': original_metrics,
                'improved_metrics': original_metrics,  # Same as original since no improvement
                'improvement': 0.0  # No improvement
            }
        
        results.append(result)
    
    return results

def process_all_questions_with_metrics(csv_file: str = "questions.csv", sample_size: int = 100) -> Dict:
    """
    Process a sample of all questions from CSV and show comprehensive metrics statistics.
    
    Args:
        csv_file: Path to the CSV file (default: "questions.csv")
        sample_size: Number of questions to sample (default: 100)
    
    Returns:
        Dictionary with comprehensive statistics
    """
    print(f"\n📊 PROCESSING ALL QUESTIONS WITH METRICS")
    print("=" * 60)
    print(f"📋 Sampling {sample_size} questions from {csv_file}")
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        print(f"📊 Loaded {len(df)} total questions from CSV")
        
        # Sample questions
        if sample_size > len(df):
            sample_size = len(df)
        
        sampled_df = df.sample(n=sample_size, random_state=42)
        
        results = []
        improvements_by_type = {}
        
        for i, (idx, row) in enumerate(sampled_df.iterrows(), 1):
            # Combine text + lexical_path
            text = str(row['text']).strip()
            lexical_path = str(row.get('lexical_path', '')).strip()
            
            if lexical_path == 'nan' or lexical_path == '':
                question_text = text
            else:
                question_text = text + " " + lexical_path
            
            question_text = question_text.strip()
            question_type = row.get('type', '')
            
            if not question_text or question_text == 'nan':
                continue
            
            # Process with template matching
            if question_type in PROMPT_TEMPLATES:
                templates = PROMPT_TEMPLATES[question_type]
                template, match_obj = match_question_to_template_simple(question_text, templates)
                
                if template and match_obj:
                    nicer_text = transform_question_with_template_simple(question_text, template, match_obj)
                    matched = True
                else:
                    nicer_text = question_text
                    matched = False
            else:
                nicer_text = question_text
                matched = False
            
            # Calculate metrics
            original_metrics = calculate_metrics_for_text(question_text)
            improved_metrics = calculate_metrics_for_text(nicer_text)
            
            # Calculate improvements
            original_avg = (original_metrics['clarity'] + original_metrics['conciseness'] + 
                          original_metrics['technical_accuracy'] + original_metrics['actionability']) / 4
            improved_avg = (improved_metrics['clarity'] + improved_metrics['conciseness'] + 
                          improved_metrics['technical_accuracy'] + improved_metrics['actionability']) / 4
            improvement = improved_avg - original_avg
            
            result = {
                'id': row.get('id', idx),
                'original_text': question_text,
                'improved_text': nicer_text,
                'type': question_type,
                'matched': matched,
                'original_metrics': original_metrics,
                'improved_metrics': improved_metrics,
                'improvement': improvement
            }
            results.append(result)
            
            # Track improvements by type
            if question_type not in improvements_by_type:
                improvements_by_type[question_type] = []
            improvements_by_type[question_type].append(improvement)
            
            # Check for error traceback
            if result.get('error_traceback') and str(result['error_traceback']).strip() != '':
                # Track error tracebacks if needed
                pass
            
            # Progress indicator
            if i % 10 == 0:
                print(f"   Processed {i}/{sample_size} questions...")
        
        # Calculate overall statistics
        all_improvements = [r['improvement'] for r in results if r['matched']]
        matched_count = sum(1 for r in results if r['matched'])
        
        print(f"\n📈 COMPREHENSIVE METRICS SUMMARY")
        print("=" * 60)
        print(f"📊 Overall Statistics:")
        print(f"   Total questions processed: {len(results)}")
        print(f"   Questions matched with templates: {matched_count}")
        print(f"   Match rate: {matched_count/len(results)*100:.1f}%")
        
        if all_improvements:
            avg_improvement = sum(all_improvements) / len(all_improvements)
            max_improvement = max(all_improvements)
            min_improvement = min(all_improvements)
            positive_improvements = sum(1 for imp in all_improvements if imp > 0)
            
            print(f"   Average improvement (matched questions): {avg_improvement:+.3f}")
            print(f"   Best improvement: {max_improvement:+.3f}")
            print(f"   Worst improvement: {min_improvement:+.3f}")
            print(f"   Questions with positive improvement: {positive_improvements}/{len(all_improvements)}")
            print(f"   Positive improvement rate: {positive_improvements/len(all_improvements)*100:.1f}%")
        
        # Show improvements by question type
        print(f"\n📋 Improvements by Question Type:")
        for question_type, improvements in improvements_by_type.items():
            if improvements:
                type_matched = len(improvements)
                type_avg_improvement = sum(improvements) / len(improvements)
                type_positive = sum(1 for imp in improvements if imp > 0)
                
                print(f"   {question_type}:")
                print(f"      Count: {type_matched}")
                print(f"      Avg improvement: {type_avg_improvement:+.3f}")
                print(f"      Positive rate: {type_positive/type_matched*100:.1f}%")
        
        return {
            'total_processed': len(results),
            'matched_count': matched_count,
            'match_rate': matched_count/len(results)*100 if results else 0,
            'avg_improvement': avg_improvement if all_improvements else 0,
            'improvements_by_type': improvements_by_type,
            'results': results
        }
        
    except FileNotFoundError:
        print(f"❌ Error: {csv_file} file not found")
        return {}
    except Exception as e:
        print(f"❌ Error processing CSV: {e}")
        return {}

def should_polish_with_ollama(metrics: Dict[str, float], threshold: float = 9.0) -> bool:
    """
    Determine if a question should be polished with Ollama based on its metrics.
    
    Args:
        metrics: Dictionary containing metric scores
        threshold: Minimum enhanced score threshold (default: 9.0)
        
    Returns:
        True if enhanced score is below threshold, False otherwise
    """
    # Calculate enhanced score (average of the four main metrics)
    enhanced_score = sum([
        metrics.get('clarity', 0.0),
        metrics.get('conciseness', 0.0),
        metrics.get('technical_accuracy', 0.0),
        metrics.get('actionability', 0.0)
    ]) / 4
    
    return enhanced_score < threshold

def polish_low_scoring_questions(question_text: str, template_metrics: Dict[str, float], 
                               question_type: str = "", error_traceback: str = "") -> str:
    """
    Automatically polish questions with template-enhanced scores below 9.0 using Ollama.
    
    Args:
        question_text: The template-improved question text
        template_metrics: Dictionary of template-improved metric scores
        question_type: Type of question (optional)
        error_traceback: Error traceback if available (optional)
        
    Returns:
        Polished question text or original if polishing fails
    """
    if not OLLAMA_AVAILABLE or not polish_question_with_fallback:
        print("   ⚠️  Ollama not available for polishing")
        return question_text
    
    # Check if enhanced score is below threshold
    if not should_polish_with_ollama(template_metrics, threshold=9.0):
        return question_text
    
    # Calculate enhanced score for display
    enhanced_score = sum([
        template_metrics.get('clarity', 0.0),
        template_metrics.get('conciseness', 0.0),
        template_metrics.get('technical_accuracy', 0.0),
        template_metrics.get('actionability', 0.0)
    ]) / 4
    
    print(f"   🔧 Polishing with Ollama (template enhanced score {enhanced_score:.3f} below 9.0)")
    
    # Prepare diagnostics for Ollama
    diagnostics = {
        "clarity_score": template_metrics.get('clarity', 0.0),
        "conciseness_score": template_metrics.get('conciseness', 0.0),
        "technical_accuracy_score": template_metrics.get('technical_accuracy', 0.0),
        "actionability_score": template_metrics.get('actionability', 0.0),
        "enhanced_score": enhanced_score,
        "error_traceback": error_traceback
    }
    
    try:
        # Try to polish with Ollama
        polished_text = polish_question_with_fallback(question_text, diagnostics)
        
        if polished_text != question_text:
            print(f"   ✅ Ollama polishing successful")
            return polished_text
        else:
            print(f"   ⚠️  Ollama polishing returned original text")
            return question_text
            
    except Exception as e:
        print(f"   ❌ Ollama polishing failed: {e}")
        return question_text

def process_random_questions_with_ollama_polishing(num_questions: int = 10, csv_file: str = "questions.csv") -> List[Dict]:
    """
    Process random questions with automatic Ollama polishing for low-scoring questions.
    
    Args:
        num_questions: Number of random questions to process
        csv_file: Path to the CSV file
    
    Returns:
        List of dictionaries containing processed question data with Ollama polishing results
    """
    questions = get_random_questions_from_csv(num_questions, csv_file)
    results = []
    
    for i, question_data in enumerate(questions, 1):
        question_text = question_data['combined_text']
        question_type = question_data['type']
        error_traceback = question_data.get('error_traceback', '')
        
        print(f"\n{'='*60}")
        print(f"📝 QUESTION {i}/{len(questions)}: {question_text[:80]}{'...' if len(question_text) > 80 else ''}")
        print(f"   Type: {question_type}")
        
        # Calculate original metrics
        original_metrics = calculate_metrics_for_text(question_text)
        
        # Check if template matching is available
        template_improved_text = question_text
        template_matched = False
        
        if question_type in PROMPT_TEMPLATES:
            templates = PROMPT_TEMPLATES[question_type]
            template, match_obj = match_question_to_template_simple(question_text, templates)
            
            if template and match_obj:
                template_improved_text = transform_question_with_template_simple(question_text, template, match_obj)
                template_matched = True
                print(f"   ✅ Template matched: {template['original']}")
                print(f"   🔍 Regex groups: {match_obj.groups()}")
            else:
                print(f"   ❌ No template match found")
        else:
            print(f"   ⚠️  No templates for type: {question_type}")
        
        # Calculate template-improved metrics
        template_metrics = calculate_metrics_for_text(template_improved_text)
        
        # Calculate template enhanced score
        template_enhanced_score = sum([
            template_metrics.get('clarity', 0.0),
            template_metrics.get('conciseness', 0.0),
            template_metrics.get('technical_accuracy', 0.0),
            template_metrics.get('actionability', 0.0)
        ]) / 4
        
        # Check if Ollama polishing is needed based on template-enhanced score
        ollama_improved_text = template_improved_text
        ollama_used = False
        
        # FIRST check if no template matched
        if not template_matched:
            print(f"   🔧 No template matched - forcing Ollama polishing")
            ollama_improved_text = polish_low_scoring_questions(
                template_improved_text, 
                template_metrics, 
                question_type, 
                error_traceback
            )
            ollama_used = (ollama_improved_text != template_improved_text)
        # SECOND check if template matched but score is low
        elif should_polish_with_ollama(template_metrics, threshold=9.0):
            print(f"   📊 Template enhanced score {template_enhanced_score:.3f} below 9.0 threshold:")
            for metric, score in template_metrics.items():
                if metric in ['clarity', 'conciseness', 'technical_accuracy', 'actionability']:
                    print(f"      {metric}: {score:.3f}")
            
            ollama_improved_text = polish_low_scoring_questions(
                template_improved_text, 
                template_metrics, 
                question_type, 
                error_traceback
            )
            ollama_used = (ollama_improved_text != template_improved_text)
        else:
            print(f"   ✅ Template enhanced score {template_enhanced_score:.3f} above 9.0 threshold - no Ollama polishing needed")
        
        # Calculate final metrics
        final_metrics = calculate_metrics_for_text(ollama_improved_text)
        
        # Calculate improvements
        template_improvement = sum([
            template_metrics.get('clarity', 0) - original_metrics.get('clarity', 0),
            template_metrics.get('conciseness', 0) - original_metrics.get('conciseness', 0),
            template_metrics.get('technical_accuracy', 0) - original_metrics.get('technical_accuracy', 0),
            template_metrics.get('actionability', 0) - original_metrics.get('actionability', 0)
        ]) / 4
        
        final_improvement = sum([
            final_metrics.get('clarity', 0) - original_metrics.get('clarity', 0),
            final_metrics.get('conciseness', 0) - original_metrics.get('conciseness', 0),
            final_metrics.get('technical_accuracy', 0) - original_metrics.get('technical_accuracy', 0),
            final_metrics.get('actionability', 0) - original_metrics.get('actionability', 0)
        ]) / 4
        
        # Display metrics comparison
        print(f"\n📊 METRICS COMPARISON:")
        print(f"   📝 Original: {question_text}")
        print(f"   📈 Original Metrics: Clarity={original_metrics['clarity']:.3f}, Conciseness={original_metrics['conciseness']:.3f}, Technical={original_metrics['technical_accuracy']:.3f}, Actionability={original_metrics['actionability']:.3f}")
        
        if template_matched:
            print(f"   ✨ Template Improved: {template_improved_text}")
            print(f"   📈 Template Metrics: Clarity={template_metrics['clarity']:.3f}, Conciseness={template_metrics['conciseness']:.3f}, Technical={template_metrics['technical_accuracy']:.3f}, Actionability={template_metrics['actionability']:.3f}")
            print(f"   📈 Template Enhanced Score: {template_enhanced_score:.3f}")
            print(f"   📈 Template Improvement: {template_improvement:+.3f}")
        
        if ollama_used:
            print(f"   🤖 Ollama Improved: {ollama_improved_text}")
            print(f"   📈 Final Metrics: Clarity={final_metrics['clarity']:.3f}, Conciseness={final_metrics['conciseness']:.3f}, Technical={final_metrics['technical_accuracy']:.3f}, Actionability={final_metrics['actionability']:.3f}")
            print(f"   📈 Final Improvement: {final_improvement:+.3f}")
            print(f"   📈 Ollama Additional Improvement: {final_improvement - template_improvement:+.3f}")
        
        result = {
            **question_data,
            'original_metrics': original_metrics,
            'template_improved_text': template_improved_text,
            'template_metrics': template_metrics,
            'template_enhanced_score': template_enhanced_score,
            'template_matched': template_matched,
            'ollama_improved_text': ollama_improved_text,
            'final_metrics': final_metrics,
            'ollama_used': ollama_used,
            'template_improvement': template_improvement,
            'final_improvement': final_improvement,
            'ollama_additional_improvement': final_improvement - template_improvement if ollama_used else 0.0
        }
        
        results.append(result)
    
    return results

def test_ollama_polishing():
    """Test the Ollama polishing functionality."""
    print("\n🤖 Testing Ollama Polishing for Low-Scoring Questions")
    print("=" * 60)
    
    # Check if Ollama is available
    if not OLLAMA_AVAILABLE:
        print("⚠️  Ollama not available. Skipping Ollama polishing tests.")
        print("   To enable Ollama polishing:")
        print("   1. Install Ollama from https://ollama.ai")
        print("   2. Start Ollama: ollama serve")
        print("   3. Pull a model: ollama pull llama2")
        return
    
    # Process a few questions with Ollama polishing
    results = process_random_questions_with_ollama_polishing(3)
    
    if results:
        print(f"\n📊 OLLAMA POLISHING SUMMARY:")
        template_improvements = []
        ollama_improvements = []
        ollama_used_count = 0
        
        for result in results:
            if result['ollama_used']:
                ollama_used_count += 1
                template_improvements.append(result['template_improvement'])
                ollama_improvements.append(result['final_improvement'])
        
        if template_improvements:
            avg_template_improvement = sum(template_improvements) / len(template_improvements)
            avg_ollama_improvement = sum(ollama_improvements) / len(ollama_improvements)
            avg_additional_improvement = avg_ollama_improvement - avg_template_improvement
            
            print(f"   📈 Questions processed: {len(results)}")
            print(f"   🤖 Ollama polishing used: {ollama_used_count}/{len(results)}")
            print(f"   📊 Average template improvement: {avg_template_improvement:+.3f}")
            print(f"   📊 Average final improvement: {avg_ollama_improvement:+.3f}")
            print(f"   📊 Average Ollama additional improvement: {avg_additional_improvement:+.3f}")
            
            if avg_additional_improvement > 0:
                print(f"   ✅ Ollama polishing provided additional improvement")
            else:
                print(f"   ⚠️  Ollama polishing did not provide additional improvement")

if __name__ == "__main__":
    print("🚀 Starting Simple Regex Testing Suite")
    print("="*50)
    
    # Test random question functions
    test_random_questions()
    
    # Test metrics comparison
    test_metrics_comparison()
    
    # Test Ollama polishing
    test_ollama_polishing()
    
    # Test comprehensive metrics analysis
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE METRICS ANALYSIS")
    print("="*60)
    process_all_questions_with_metrics(sample_size=50)
    
    print("\n🎉 All tests completed!")
    print("\n📋 SUMMARY OF NEW FUNCTIONALITY:")
    print("   ✅ Metrics calculation for original vs improved text")
    print("   ✅ Detailed metrics comparison display")
    print("   ✅ Process random questions with metrics")
    print("   ✅ Comprehensive statistics across all question types")
    print("   ✅ Improvement tracking by question type")
    print("   ✅ Overall performance metrics")
    print("   🤖 Automatic Ollama polishing for questions with scores below 9.0")
    print("   📊 Template + Ollama improvement comparison")