import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = None
MAX_OUTPUT_TOKENS = int(os.getenv("GROQ_MAX_OUTPUT_TOKENS", "2048"))

def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    return _client

DEFAULT_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

def generate_pytest_for_file(filename: str, original_code: str, functions: list, model: str = DEFAULT_MODEL) -> str:
    """Call LLM to generate a pytest suite for the provided Python code.

    Args:
        filename: Name of the original file (used for imports).
        original_code: Full source of the Python file.
        functions: List of function dicts from parser results.
        model: Groq model ID to use.

    Returns:
        str: The generated pytest code.
    """
    
    # Clean filename for import (e.g. remove .py)
    module_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
    # Fix: Replace slashes with dots for nested module imports
    module_name = module_name.replace("/", ".").replace("\\", ".")
    
    func_signatures = []
    for f in functions:
        cname = f.get('class_name')
        if cname:
            func_signatures.append(f"- {cname}.{f['name']}() (Method)")
        else:
            func_signatures.append(f"- {f['name']}() (Top-level Function)")
        
    func_list = "\n".join(func_signatures)

    SYSTEM_PROMPT = f'''You are a Python QA Engineer specializing in writing high-quality pytest suites.
You will receive the source code of a Python module and a list of functions/methods it contains.
You MUST output a COMPLETE pytest file wrapped in a ```python code block.

GENERATION RULES:
1. STRICT IMPORT: Your pytest suite MUST start with exactly these two lines:
   ```python
   import pytest
   from {module_name} import *
   ```
2. COVERAGE: Generate at least 2-3 test cases for each function/method provided in the list.
3. CLASSES & METHODS: If a function is a method of a class, you MUST instantiate the class (e.g., `obj = ClassName()`) before calling the method (`obj.method_name()`).
4. EDGE CASES: Include edge cases ONLY when they are clearly supported by the source code or are a direct consequence of the implementation. Do NOT add speculative cases just to increase coverage.
5. MOCKING: If the code uses external APIs or complex dependencies, use `unittest.mock` to mock them.
6. FLOATS & PRECISION: WARNING: NEVER hardcode decimal values that you manually truncated (e.g., writing `24.69` for `24.6913...`). You MUST either use the exact formula (e.g., `pytest.approx(80 / 1.8**2)`) OR use at least 10 decimal places of precision.
7. EXCEPTIONS & CRASHES: CRITICAL: Never assume a function validates inputs unless you see `raise` statements in the source code. If the source code does not explicitly `raise` an error, DO NOT WRITE A TEST expecting `pytest.raises`. Hallucinated exception tests cause failures.
8. TRANSPARENCY: Every assertion should ideally have a meaningful error message.
9. NO ACTUAL EXECUTION: Do not include `if __name__ == "__main__":`.
10. EXPECTED VALUES MUST BE DERIVED, NOT GUESSED: For string-formatting/concatenation functions, build expected values using the same deterministic expression pattern (e.g., `"Hello, " + name + "!" * excitement`) instead of hand-typed literals that can be off by one character.
11. NAN HANDLING: Never assert `x == float('nan')` or `pytest.approx(float('nan'))`. If NaN behavior is tested, use `math.isnan(x)`.
12. SOURCE-GROUNDED BEHAVIOR ONLY: Do not invent validation rules, business rules, fallback behavior, or normalization behavior unless it is directly visible in the source code.
13. AVOID EXOTIC INPUTS BY DEFAULT: Do not use NaN, infinity, -0.0, extremely large numbers, random strings, or empty strings unless the source code clearly suggests those cases matter.
14. STRING OUTPUTS: For string-producing functions, prefer representative normal inputs. Only include empty-string or unusual formatting cases when the exact output is obvious from the implementation.
15. PRINTING/SIDE EFFECTS: If a function prints or writes output, assert only the observable output that is clearly produced by the source code. Do not invent extra formatting expectations.
16. PREFER RELIABLE TESTS OVER MAXIMUM COUNT: It is better to produce fewer correct tests than more brittle or speculative ones.

CODE STRUCTURE:
```python
import pytest
from {module_name} import *

# Tests follow...
```

OUTPUT RULE: Return ONLY a single ```python code block containing the full test suite. No explanations or commentary.'''

    prompt = f"""Generate a comprehensive pytest suite for the module `{filename}`.

FUNCTIONS & METHODS TO TEST:
{func_list}

SOURCE CODE:
```python
{original_code}
```

Remember: 
- Start with `import pytest` and `from {module_name} import *`.
- Instantiate classes for methods.
- Provide multiple test cases per function, but only for behavior clearly supported by the source code.
- Derive expected values from the implementation instead of guessing literals.
- Avoid speculative edge cases unless the source explicitly supports them.
- Output ONLY the ```python code block."""

    client = get_client()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.05,
            max_tokens=MAX_OUTPUT_TOKENS,
        )
        
        test_code = response.choices[0].message.content.strip()
        
        # Strip reasoning blocks
        test_code = re.sub(r'<think>.*?</think>', '', test_code, flags=re.DOTALL | re.IGNORECASE).strip()
        
        # Extract from markdown fences
        all_matches = re.findall(r'```(?:python)?\n?(.*?)\n?```', test_code, flags=re.DOTALL | re.IGNORECASE)
        if all_matches:
            test_code = max(all_matches, key=len).strip()
            
        # --- ROBUST FAIL-SAFE IMPORT INJECTOR (Prepend & Cleanup) ---
        # 1. Strip any existing module-wide imports to avoid duplicates
        import_pattern = rf'^\s*from\s+{re.escape(module_name)}\s+import.*$'
        test_code = re.sub(import_pattern, '', test_code, flags=re.MULTILINE)
        
        # 2. Strip any existing 'import pytest'
        test_code = re.sub(r'^\s*import\s+pytest\s*$', '', test_code, flags=re.MULTILINE)
        
        # 3. Prepend the guaranteed header
        header = f"import pytest\nfrom {module_name} import *\n\n"
        test_code = header + test_code.strip()
            
        return test_code
    except Exception as e:
        return f"# Error generating tests: {str(e)}"
