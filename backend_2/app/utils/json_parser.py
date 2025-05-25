import json
import re
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

def extract_json_from_markdown(text: str) -> Optional[str]:
    """
    Extracts JSON string from markdown code blocks.
    Handles ```json ... ``` or just ``` ... ```.
    """
    # Regex to find JSON within ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def robust_json_parser(json_string: str, context: str = "Unknown") -> Optional[Any]:
    """
    Robustly parses a JSON string, attempting to handle common LLM output issues.
    
    Args:
        json_string (str): The string potentially containing JSON.
        context (str): A string describing the context of parsing (e.g., "DB Schema Design").
        
    Returns:
        Optional[Any]: Parsed JSON object or None if parsing fails.
    """
    if not isinstance(json_string, str):
        logger.warning(f"Robust JSON parser received non-string input in context '{context}': {type(json_string)}")
        return None

    original_string = json_string # Keep a copy for logging if all attempts fail

    # Attempt 1: Direct parsing
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        pass # Continue to next attempt

    # Attempt 2: Extract from markdown code block
    extracted_json = extract_json_from_markdown(json_string)
    if extracted_json:
        try:
            return json.loads(extracted_json)
        except json.JSONDecodeError:
            # If markdown extraction also fails, log it and try to clean the extracted_json
            json_string = extracted_json # Use the extracted content for further cleaning
            pass 
    
    # Attempt 3: Try to find JSON object or array within the string
    # This handles cases where there might be leading/trailing text not in a code block
    obj_match = re.search(r"\{[\s\S]*\}", json_string)
    arr_match = re.search(r"\[[\s\S]*\]", json_string)

    json_candidate = None
    if obj_match and arr_match:
        # If both object and array are found, pick the one that starts earlier
        if obj_match.start() < arr_match.start():
            json_candidate = obj_match.group(0)
        else:
            json_candidate = arr_match.group(0)
    elif obj_match:
        json_candidate = obj_match.group(0)
    elif arr_match:
        json_candidate = arr_match.group(0)

    if json_candidate:
        try:
            return json.loads(json_candidate)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse extracted JSON candidate in context '{context}'. Error: {e}. Candidate: {json_candidate[:200]}...")
            # Fall through to final log if this also fails
    
    logger.error(f"All attempts to parse JSON failed in context '{context}'. Original input (first 500 chars): {original_string[:500]}")
    return None

if __name__ == '__main__':
    # Test cases
    test_strings = [
        ('{"key": "value", "number": 123}', "Simple JSON object"),
        ('[1, 2, "three"]', "Simple JSON array"),
        ('Some text before ```json\n{"key": "value"}\n``` and after.', "Markdown JSON"),
        ('```\n{"key": "markdown no lang"}\n```', "Markdown JSON no lang"),
        ('This is not JSON.', "Plain text, no JSON"),
        ('{"bad": json, }', "Malformed JSON (trailing comma, unquoted value) - expect fail"),
        ('Explanation: \n{"key": "value with explanation"}', "JSON with leading text"),
        ('{"key": "value with trailing text"}\nSome trailing notes.', "JSON with trailing text"),
        ('```json\n{\n  "user_stories": [\n    {\n      "role": "Database Administrator",\n      "goal": "Create a \'users\' table",\n      "benefit": "Ensure efficient user auth"\n    }\n  ]\n}\n```', "Real-world example")
    ]

    for s, desc in test_strings:
        print(f"\nTesting: {desc}")
        print(f"Input: {s[:100]}...")
        parsed = robust_json_parser(s, context=f"Test - {desc}")
        if parsed:
            print(f"Parsed: {json.dumps(parsed, indent=2)[:200]}...")
        else:
            print("Parsed: None")
