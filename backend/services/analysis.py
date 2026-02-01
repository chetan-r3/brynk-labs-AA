"""
Analysis Service - LLM-based issue extraction

Extracts structured issues from customer transcripts using LLM reasoning.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from pydantic import BaseModel, ValidationError
import openai
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


# Issue schema for validation
class Issue(BaseModel):
    """Schema for a single extracted issue"""
    title: str
    details: str
    evidence: List[str]


class IssuesResponse(BaseModel):
    """Schema for issues extraction response"""
    issues: List[Issue]


# Initialize OpenAI client
_client = None


def get_openai_client() -> OpenAI:
    """Get or create OpenAI client (singleton pattern)."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. "
                "Please set it to use issue extraction: export OPENAI_API_KEY='your-key'"
            )
        # Strip any whitespace/newlines from the API key
        api_key = api_key.strip()
        _client = OpenAI(api_key=api_key)
    return _client


def extract_issues(
    customer_transcript: str,
    model: str = "gpt-4o-mini",
    max_retries: int = 3
) -> List[Dict[str, any]]:
    """
    Extract structured issues from customer transcript using LLM.
    
    This function uses LLM reasoning (not training) to identify issues,
    complaints, and problems mentioned by the customer.
    
    Args:
        customer_transcript: Customer-only transcript text
        model: OpenAI model to use (default: "gpt-4o-mini" for cost efficiency)
        max_retries: Maximum number of retries if JSON validation fails
        
    Returns:
        List of issue dictionaries with "title", "details", and "evidence" keys
        
    Example:
        [
            {
                "title": "Refund delay",
                "details": "Refund not received in 10 days",
                "evidence": ["I still haven't got my refund"]
            }
        ]
        
    Raises:
        ValueError: If OpenAI API key is not set
        Exception: If extraction fails after retries
    """
    if not customer_transcript or not customer_transcript.strip():
        return []
    
    client = get_openai_client()
    
    # System prompt that forces JSON output
    system_prompt = """You are an expert at analyzing customer service calls and extracting structured issues.

Your task is to analyze the customer's transcript and extract all issues, complaints, and problems they mentioned.

Rules:
1. Extract ONLY issues/problems/complaints (not positive feedback)
2. Each issue must have:
   - title: Short, clear title (e.g., "Refund delay", "App crashing")
   - details: More detailed description
   - evidence: List of exact quotes from the transcript that support this issue
3. Be specific and accurate
4. Group related complaints into single issues
5. You MUST respond with valid JSON only, no other text

Output format (JSON object with "issues" array):
{
  "issues": [
    {
      "title": "Issue title",
      "details": "Detailed description",
      "evidence": ["quote 1", "quote 2"]
    }
  ]
}"""

    user_prompt = f"""Analyze this customer transcript and extract all issues, complaints, and problems:

{customer_transcript}

Return ONLY valid JSON object with "issues" array. No explanations, no markdown, just JSON."""

    # Retry loop for JSON validation
    for attempt in range(max_retries):
        try:
            # Check if model supports JSON mode
            use_json_mode = model.startswith("gpt-4") or "o1" in model
            
            # Call OpenAI API
            api_params = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,  # Lower temperature for more consistent JSON
            }
            
            if use_json_mode:
                api_params["response_format"] = {"type": "json_object"}
            
            response = client.chat.completions.create(**api_params)
            
            # Extract content
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON
            parsed = json.loads(content)
            
            # Extract issues array (handle both {"issues": [...]} and direct array)
            if isinstance(parsed, dict):
                issues_data = parsed.get("issues", [])
            elif isinstance(parsed, list):
                issues_data = parsed
            else:
                issues_data = []
            
            # Ensure it's a list
            if not isinstance(issues_data, list):
                issues_data = [issues_data] if issues_data else []
            
            # Validate schema using Pydantic
            validated_issues = []
            for issue_data in issues_data:
                try:
                    issue = Issue(**issue_data)
                    validated_issues.append(issue.dict())
                except ValidationError as e:
                    # Skip invalid issues but log
                    print(f"Warning: Skipping invalid issue: {e}")
                    continue
            
            return validated_issues
            
        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                print(f"JSON parse error (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"Response was: {content[:200]}...")
                continue
            else:
                raise Exception(
                    f"Failed to parse JSON after {max_retries} attempts. "
                    f"Last error: {str(e)}. Response: {content[:500]}"
                )
        except ValidationError as e:
            if attempt < max_retries - 1:
                print(f"Validation error (attempt {attempt + 1}/{max_retries}): {e}")
                continue
            else:
                raise Exception(f"Schema validation failed after {max_retries} attempts: {str(e)}")
        except openai.APIError as e:
            # Handle OpenAI API errors specifically
            error_code = getattr(e, 'status_code', None)
            error_type = getattr(e, 'type', None)
            error_message = str(e)
            
            if error_code == 429:
                if error_type == 'insufficient_quota':
                    raise Exception(
                        f"OpenAI API quota exceeded. Please check:\n"
                        f"1. Your OpenAI account has available credits\n"
                        f"2. Your billing is set up correctly\n"
                        f"3. Visit: https://platform.openai.com/account/billing\n"
                        f"Original error: {error_message}"
                    )
                else:
                    raise Exception(
                        f"OpenAI API rate limit exceeded. Please try again later.\n"
                        f"Original error: {error_message}"
                    )
            else:
                raise Exception(
                    f"OpenAI API error (code {error_code}): {error_message}\n"
                    f"Please check your API key and account status."
                )
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Error (attempt {attempt + 1}/{max_retries}): {e}")
                continue
            else:
                raise Exception(f"Issue extraction failed after {max_retries} attempts: {str(e)}")
    
    return []


def classify_tone(
    customer_transcript: str,
    model: str = "gpt-4o-mini",
    max_retries: int = 3
) -> Dict[str, any]:
    """
    Classify the overall tone of the customer transcript.
    
    Args:
        customer_transcript: Customer-only transcript text
        model: OpenAI model to use (default: "gpt-4o-mini")
        max_retries: Maximum number of retries if JSON validation fails
        
    Returns:
        Dictionary with "label", "confidence", and "evidence" keys
        
    Example:
        {
            "label": "Frustrated",
            "confidence": 0.76,
            "evidence": ["Repeated complaints", "Urgent wording"]
        }
    """
    if not customer_transcript or not customer_transcript.strip():
        return {
            "label": "Calm",
            "confidence": 0.5,
            "evidence": ["No customer transcript available"]
        }
    
    client = get_openai_client()
    
    # System prompt for tone classification
    system_prompt = """You are an expert at analyzing customer service calls and classifying customer tone.

Your task is to analyze the customer's transcript and classify their overall emotional tone.

Allowed tone labels (choose ONE):
- Calm: Customer is composed, polite, and measured in their communication
- Frustrated: Customer shows signs of annoyance, repeated complaints, or impatience
- Angry: Customer displays strong negative emotions, harsh language, or hostility
- Anxious: Customer shows worry, uncertainty, or concern about their situation

You MUST respond with valid JSON only, no other text.

Output format (JSON object):
{
  "label": "Frustrated",
  "confidence": 0.76,
  "evidence": ["Repeated complaints", "Urgent wording"]
}

Confidence should be between 0.0 and 1.0.
Evidence should be 2-3 short phrases describing why this tone was chosen."""

    user_prompt = f"""Analyze this customer transcript and classify the overall tone:

{customer_transcript}

Return ONLY valid JSON object with "label", "confidence", and "evidence" fields. No explanations, no markdown, just JSON."""

    # Retry loop
    for attempt in range(max_retries):
        try:
            # Check if model supports JSON mode
            use_json_mode = model.startswith("gpt-4") or "o1" in model
            
            # Call OpenAI API
            api_params = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,
            }
            
            if use_json_mode:
                api_params["response_format"] = {"type": "json_object"}
            
            response = client.chat.completions.create(**api_params)
            
            # Extract content
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON
            parsed = json.loads(content)
            
            # Validate required fields
            label = parsed.get("label", "Calm")
            confidence = float(parsed.get("confidence", 0.5))
            evidence = parsed.get("evidence", [])
            
            # Validate label is one of allowed values
            allowed_labels = ["Calm", "Frustrated", "Angry", "Anxious"]
            if label not in allowed_labels:
                label = "Calm"  # Default fallback
            
            # Clamp confidence to 0-1
            confidence = max(0.0, min(1.0, confidence))
            
            # Ensure evidence is a list
            if not isinstance(evidence, list):
                evidence = [evidence] if evidence else []
            
            return {
                "label": label,
                "confidence": round(confidence, 2),
                "evidence": evidence
            }
            
        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                print(f"Tone classification JSON parse error (attempt {attempt + 1}/{max_retries}): {e}")
                continue
            else:
                # Return default on final failure
                return {
                    "label": "Calm",
                    "confidence": 0.5,
                    "evidence": ["Unable to classify tone"]
                }
        except openai.APIError as e:
            if attempt < max_retries - 1:
                print(f"Tone classification API error (attempt {attempt + 1}/{max_retries}): {e}")
                continue
            else:
                # Return default on final failure
                return {
                    "label": "Calm",
                    "confidence": 0.5,
                    "evidence": ["API error during tone classification"]
                }
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Tone classification error (attempt {attempt + 1}/{max_retries}): {e}")
                continue
            else:
                # Return default on final failure
                return {
                    "label": "Calm",
                    "confidence": 0.5,
                    "evidence": ["Error during tone classification"]
                }
    
    # Final fallback
    return {
        "label": "Calm",
        "confidence": 0.5,
        "evidence": ["Classification failed"]
    }


def format_issues_for_display(issues: List[Dict[str, any]]) -> str:
    """
    Format issues for human-readable display.
    
    Args:
        issues: List of issue dictionaries
        
    Returns:
        Formatted string
    """
    if not issues:
        return "No issues found."
    
    lines = []
    for i, issue in enumerate(issues, 1):
        lines.append(f"\n{i}. {issue.get('title', 'Unknown')}")
        lines.append(f"   Details: {issue.get('details', 'N/A')}")
        evidence = issue.get('evidence', [])
        if evidence:
            lines.append(f"   Evidence:")
            for quote in evidence:
                lines.append(f"     - \"{quote}\"")
    
    return "\n".join(lines)
