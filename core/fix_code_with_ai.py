import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    return _client

AVAILABLE_MODELS = {
    "llama-3.3-70b-versatile":                    "⚡ Llama 3.3 70B",
    "openai/gpt-oss-120b":                         "🧠 GPT-OSS 120B (Default)",
    "qwen/qwen3-32b":                              "🌊 Qwen3 32B",
    "moonshotai/kimi-k2-instruct":                 "🌙 Kimi K2",
}

DEFAULT_MODEL = "openai/gpt-oss-120b"


def fix_docstrings(original_code: str, functions_with_errors: list, model: str = DEFAULT_MODEL, style: str = "Google", filename: str = "module.py") -> tuple:
    """Call LLM to fix docstring errors and generate cached tests.

    Args:
        original_code: Full source of the Python file.
        functions_with_errors: List of function dicts from parser results.
        model: Groq model ID to use for the fix.
        style: The target docstring style format (e.g., Google, NumPy, reST).
        filename: The source filename, used to derive the import name for tests.

    Returns:
        tuple: (fixed_python_code, cached_pytest_suite)
    """
    module_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
    error_lines = []
    FIX_HINTS = {
        "D401": "Use imperative mood. WRONG: 'Hashes the password', 'Reading rows'. RIGHT: 'Hash the password.', 'Read rows.'",
        "D400": "First line must end with a period.",
        "D415": "First line must end with period, question mark, or exclamation mark.",
        "D403": "First word must be capitalized.",
        "D404": "First word must not be 'This'.",
        "D300": "Use triple double-quotes not triple single-quotes.",
        "D205": "Add exactly one blank line between summary and description.",
        "D212": "Summary must be on the first line after the opening triple-quote, no leading blank line.",
        "DAR101": "This parameter exists in the function signature but is missing from the Args: section. Add it with its type and description.",
        "DAR201": "The return value is missing from the Returns: section. Add it with its type and description.",
        "DAR301": "The raised exception is missing from the Raises: section. Add it with its description.",
    }
    func_names = []
    for func in functions_with_errors:
        func_names.append(func['name'])
        if func.get("docstring_errors"):
            for e in func["docstring_errors"]:
                hint = FIX_HINTS.get(e['code'], "")
                suffix = f" → FIX: {hint}" if hint else ""
                error_lines.append(f"  - {func['name']}(): [{e['code']}] {e['message']}{suffix}")

    has_missing_docstrings = any(not func.get("has_docstring") for func in functions_with_errors)
    if not error_lines and not has_missing_docstrings:
        return original_code, ""

    error_summary = "\n".join(error_lines)
    func_list = ", ".join(func_names)

    SYSTEM_PROMPT = f'''You are a Python code editor specializing in PEP 257 {style}-style docstrings and pytest suites.
You will receive Python source code and a list of docstring errors to fix.
You MUST output TWO separate markdown code blocks:
1. The COMPLETE fixed Python file.
2. A COMPLETE pytest suite for all functions: {func_list}.

RULES FOR CODE FIXING:
1. Fix ONLY the violations listed in ERRORS. Do not touch unrelated code.
2. The summary MUST start on the VERY FIRST LINE immediately after the opening triple-quote. No leading blank line.
3. Every summary line MUST end with a period.
4. Every summary MUST use IMPERATIVE mood (command form).
    - WRONG: "Hashes the password", "This function reads a file", "Reading rows from CSV"
    - RIGHT:  "Hash the password.",   "Read a file.",              "Read rows from a CSV file."
    - RULE: Ask "Does this function X?" → write just "X." using the base verb form.
5. For functions with NO docstring (D103), add a complete new one in {style} style.
6. For DAR101: the parameter exists in the signature but is missing from Args: — add it.
7. For DAR201: the return value is missing from Returns: — add it.
8. For DAR301: the raised exception is missing from Raises: — add it.
9. For D300: replace triple single-quotes with triple double-quotes.
10. For D205: add exactly one blank line between the summary line and the description.
11. For D212: summary on the first line after opening triple-quote, no blank line before it.
12. Preserve all existing logic, imports, and non-docstring content exactly.

RULES FOR TEST GENERATION:
1. Your pytest suite MUST include: `import pytest` AND `from {module_name} import *`.
2. Use `pytest.approx()` for all float comparisons.
3. Test only behavior that is directly supported by the source code. Do NOT invent validation rules, crash behavior, or business rules.
4. Include edge cases only when the implementation clearly supports them or they are obvious from the source code.
5. Never assert `x == float('nan')` or `pytest.approx(float('nan'))`. If NaN behavior is tested, use `math.isnan(x)`.
6. For strings or formatted text, derive expected values from the implementation pattern instead of guessing literals.
7. Do not use exotic inputs like NaN, infinity, -0.0, huge numbers, empty strings, or None unless the code clearly shows those cases are meaningful.
8. Every assertion should have a meaningful error message.
9. If the code handles inputs gracefully (like string formatting None), DO NOT expect TypeErrors.

OUTPUT FORMAT:
```python
# Fixed Code here...
```
```python
# Pytest Suite here...
```
NO explanations or commentary.'''

    prompt = f"""Fix errors and generate tests for the code below.

ERRORS:
{error_summary}

ORIGINAL CODE:
```python
{original_code}
```"""

    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.05,
        max_tokens=8192,
    )

    content = response.choices[0].message.content.strip()
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL | re.IGNORECASE).strip()

    # Extract all python blocks
    all_blocks = re.findall(r'```(?:python)?\n?(.*?)\n?```', content, flags=re.DOTALL | re.IGNORECASE)
    
    fixed_code = original_code
    cached_tests = ""

    if len(all_blocks) >= 2:
        # Heaviest block is likely the source code, second heaviest is likely the tests
        # Or more reliably: Block 1 is Source, Block 2 is Tests (following prompt instructions)
        fixed_code = all_blocks[0].strip()
        cached_tests = all_blocks[1].strip()
    elif len(all_blocks) == 1:
        fixed_code = all_blocks[0].strip()

    # Validation check
    try:
        import ast
        ast.parse(fixed_code)
    except SyntaxError:
        fixed_code = original_code

    return fixed_code, cached_tests
