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
    "llama-3.3-70b-versatile":                    "⚡ Llama 3.3 70B (Default)",
    "openai/gpt-oss-120b":                         "🧠 GPT-OSS 120B",
    "qwen/qwen3-32b":                              "🌊 Qwen3 32B",
    "moonshotai/kimi-k2-instruct":                 "🌙 Kimi K2",
}

DEFAULT_MODEL = "llama-3.3-70b-versatile"


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
    func_names = []
    for func in functions_with_errors:
        func_names.append(func['name'])
        if func.get("docstring_errors"):
            for e in func["docstring_errors"]:
                error_lines.append(f"  - {func['name']}(): [{e['code']}] {e['message']}")

    if not error_lines:
        return original_code, ""

    error_summary = "\n".join(error_lines)
    func_list = ", ".join(func_names)

    SYSTEM_PROMPT = f'''You are a Python code editor specializing in PEP 257 {style}-style docstrings and pytest suites.
You will receive Python source code and a list of docstring errors to fix.
You MUST output TWO separate markdown code blocks:
1. The COMPLETE fixed Python file.
2. A COMPLETE pytest suite for all functions: {func_list}.

RULES FOR CODE FIXING:
1. The summary MUST start on the VERY FIRST LINE immediately after the opening triple-quote.
2. For functions with NO docstring, add a complete new one in {style} style.
3. Include Args/Returns/Raises sections as required.

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
