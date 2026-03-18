"""Debug script to log raw LLM output for each model and verify extraction logic."""

import os
import re
import ast
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

SAMPLE_CODE = '''
def add(a, b):
    return a + b

def greet(name):
    """greet someone"""
    print(f"Hello {name}")
'''

PROMPT = """You are a Python docstring expert. Fix ONLY the docstrings in the code below to resolve every listed error.

STRICT RULES — follow exactly:
- Do NOT change any logic, variable names, function signatures, imports, or any non-docstring code
- Follow PEP 257 Google style docstrings
- Every docstring must start with a one-line summary on the first line immediately after the triple quote
- You MUST wrap your ENTIRE response inside a single ```python code block. 
- DO NOT return any english explanations, conversational preamble, or any text outside of the code block.

ERRORS TO FIX:
  - add(): [DAR101] Missing 'Args:' section
  - add(): [DAR201] Missing 'Returns:' section
  - greet(): [DAR101] Missing 'Args:' section

ORIGINAL CODE:
""" + SAMPLE_CODE

MODELS = {
    "llama-3.3-70b-versatile":                      "Llama 3.3 70B",
    "openai/gpt-oss-120b":                          "GPT-OSS 120B",
    "qwen/qwen3-32b":                               "Qwen3 32B",
    "moonshotai/kimi-k2-instruct":                  "Kimi K2",
    "meta-llama/llama-4-maverick-17b-128e-instruct": "Llama 4 Maverick",
}

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

for model_id, model_name in MODELS.items():
    print(f"\n{'='*60}")
    print(f"MODEL: {model_name} ({model_id})")
    print('='*60)
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": PROMPT}],
            temperature=0.1,
            max_tokens=1024,
        )
        raw = response.choices[0].message.content.strip()

        print("\n--- RAW RESPONSE (first 500 chars) ---")
        print(repr(raw[:500]))

        # Now apply current extraction regex
        match = re.search(r'```(?:python)?\n?(.*?)\n?```', raw, flags=re.DOTALL | re.IGNORECASE)
        if match:
            extracted = match.group(1).strip('`').strip()
            print("\n--- EXTRACTED CODE ---")
            print(extracted[:300])
            # Now test AST parse
            try:
                ast.parse(extracted)
                print("\n[OK] AST parse succeeded!")
            except SyntaxError as e:
                print(f"\n[ERROR] AST SyntaxError: {e}")
                print(f"  Problem area: {repr(extracted[:200])}")
        else:
            print("\n[WARNING] No markdown fence found! Raw text used as-is.")
            # Check if raw itself is valid Python
            cleaned = raw.strip('`').strip()
            try:
                ast.parse(cleaned)
                print("[OK] Raw text IS valid Python (no fences needed).")
            except SyntaxError as e:
                print(f"[ERROR] Raw text failed AST parse too: {e}")
                
    except Exception as e:
        print(f"[GROQ API ERROR] {type(e).__name__}: {e}")

print("\n\nDone.")
