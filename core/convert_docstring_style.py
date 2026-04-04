"""Docstring style detection and conversion utilities using Groq LLM."""

import os
import re
import ast
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = None
MAX_OUTPUT_TOKENS = int(os.getenv("GROQ_MAX_OUTPUT_TOKENS", "2048"))


def get_client():
    """Return a cached Groq client, initializing lazily."""
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    return _client


# ─────────────────────────────────────────────
# Style detection
# ─────────────────────────────────────────────

def detect_style(code: str) -> str:
    """Detect the dominant docstring style used in a Python file.

    Returns:
        One of: 'Google', 'reST', 'NumPy', 'Mixed', 'None/Incomplete'.
    """
    try:
        tree = ast.parse(code)
    except Exception:
        return "None/Incomplete"

    # Walk tree once — keep function docstrings and non-function docstrings separate
    func_docstrings = []   # only from FunctionDef / AsyncFunctionDef
    other_docstrings = []  # class + module (for style scoring only, not coverage)
    total_funcs = 0

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            total_funcs += 1
            ds = ast.get_docstring(node)
            if ds:
                func_docstrings.append(ds)
        elif isinstance(node, (ast.ClassDef, ast.Module)):
            ds = ast.get_docstring(node)
            if ds:
                other_docstrings.append(ds)

    # If no docstrings at all, nothing to detect
    if not func_docstrings and not other_docstrings:
        return "None/Incomplete"

    # Coverage check — only function-level
    if total_funcs > 0 and len(func_docstrings) < total_funcs:
        return "None/Incomplete"

    # Score every docstring individually (functions first, then class/module)
    all_docstrings = func_docstrings + other_docstrings
    style_votes: dict = {"Google": 0, "reST": 0, "NumPy": 0}

    for ds in all_docstrings:
        g = sum([
            bool(re.search(r'^\s*Args:\s*$', ds, re.M)),
            bool(re.search(r'^\s*Returns:\s*$', ds, re.M)),
            bool(re.search(r'^\s*Raises:\s*$', ds, re.M)),
            bool(re.search(r'^\s*Yields:\s*$', ds, re.M)),
            bool(re.search(r'^\s*Note:\s*$', ds, re.M)),
            bool(re.search(r'^\s*Example:\s*$', ds, re.M)),
        ])
        r = sum([
            bool(re.search(r':param\s+\w+:', ds)),
            bool(re.search(r':type\s+\w+:', ds)),
            bool(re.search(r':returns?:', ds)),
            bool(re.search(r':rtype:', ds)),
            bool(re.search(r':raises\s+\w+:', ds)),
        ])
        n = sum([
            bool(re.search(r'Parameters\s*\n\s*-{3,}', ds)),
            bool(re.search(r'Returns\s*\n\s*-{3,}', ds)),
            bool(re.search(r'Raises\s*\n\s*-{3,}', ds)),
            bool(re.search(r'Yields\s*\n\s*-{3,}', ds)),
            bool(re.search(r'Notes\s*\n\s*-{3,}', ds)),
        ])

        best = max(g, r, n)
        if best > 0:
            if g >= r and g >= n:
                style_votes["Google"] += 1
            elif r >= n:
                style_votes["reST"] += 1
            else:
                style_votes["NumPy"] += 1
        # else: ambiguous single-liner — does NOT count as a style vote

    active_styles = [s for s, cnt in style_votes.items() if cnt > 0]

    if len(active_styles) == 0:
        # All docstrings are single-liners with no style markers — treat as Google convention
        return "Google"
    if len(active_styles) > 1:
        return "Mixed"
    return active_styles[0]


# ─────────────────────────────────────────────
# Style format examples (used in prompts)
# ─────────────────────────────────────────────

STYLE_EXAMPLES = {
    "Google": '''\
def add(a, b):
    """Add two numbers together.

    Args:
        a (int): The first number.
        b (int): The second number.

    Returns:
        int: The sum of a and b.

    Raises:
        TypeError: If inputs are not numeric.
    """
    return a + b''',

    "reST": '''\
def add(a, b):
    """Add two numbers together.

    :param a: The first number.
    :type a: int
    :param b: The second number.
    :type b: int
    :returns: The sum of a and b.
    :rtype: int
    :raises TypeError: If inputs are not numeric.
    """
    return a + b''',

    "NumPy": '''\
def add(a, b):
    """Add two numbers together.

    Parameters
    ----------
    a : int
        The first number.
    b : int
        The second number.

    Returns
    -------
    int
        The sum of a and b.

    Raises
    ------
    TypeError
        If inputs are not numeric.
    """
    return a + b''',
}


def _build_system_prompt(target_style: str, module_name: str = "module") -> str:
    """Build the system prompt for docstring conversion/generation."""
    example = STYLE_EXAMPLES[target_style]
    return f'''You are a Python docstring expert.
Your job is to rewrite ALL docstrings into {target_style} format.

STRICT RULES:
1. Do NOT change any logic, variable names, function signatures, imports, or non-docstring code.
2. Convert every existing docstring to {target_style} format.
3. The summary line MUST be on the first line immediately after the opening triple-quote.
4. Preserve non-docstring formatting where possible.
5. You MUST output ONE code block containing the COMPLETE Python file/function with converted docstrings.

EXACT FORMAT:
```python
# (The complete source code with {target_style} docstrings)
```
'''


def _extract_blocks(raw: str, fallback_code: str) -> tuple:
    """Extract source code and tests from LLM response."""
    # Strip <think> blocks
    cleaned = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL | re.IGNORECASE).strip()
    
    matches = re.findall(r'```(?:python)?\n?(.*?)\n?```', cleaned, flags=re.DOTALL | re.IGNORECASE)
    
    code = fallback_code
    tests = ""
    
    if len(matches) >= 2:
        code = matches[0].strip()
        tests = matches[1].strip()
    elif len(matches) == 1:
        code = matches[0].strip()
    else:
        # Fallback for raw output without backticks
        code = cleaned.strip()
        
    # Final check: if 'code' doesn't look like code or has syntax errors, fallback
    try:
        ast.parse(code)
    except Exception:
        code = fallback_code
        
    return code, tests


# Compatibility alias for static tests
def _extract_code(raw: str, fallback: str) -> str:
    """Legacy alias: only returns the first block (the code)."""
    code, _ = _extract_blocks(raw, fallback)
    return code


def convert_style(
    original_code: str,
    target_style: str,
    scope: str = "whole_file",
    func_name: str = "",
    model: str = "meta-llama/llama-4-scout-17b-16e-instruct",
    filename: str = "module.py"
) -> tuple:
    """Convert docstrings in Python code.

    Returns:
        tuple: (full_file_code, generated_tests)
    """
    module_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
    
    if scope == "function" and func_name:
        try:
            tree = ast.parse(original_code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
                    lines = original_code.splitlines()
                    func_src = "\n".join(lines[node.lineno - 1:node.end_lineno])
                    prompt_code = func_src
                    break
            else:
                prompt_code = original_code
        except Exception:
            prompt_code = original_code
    else:
        prompt_code = original_code

    sys_prompt = _build_system_prompt(target_style, module_name=module_name)
    user_prompt = f"""Convert the docstrings in the code below to {target_style} style.

CODE:
```python
{prompt_code}
```

Return the COMPLETE {'function' if scope == 'function' and func_name else 'file'} in a single code block."""

    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.05,
        max_tokens=MAX_OUTPUT_TOKENS,
    )

    raw = response.choices[0].message.content.strip()
    converted, tests = _extract_blocks(raw, prompt_code)

    # If scope is function, splice back into full file
    final_code = original_code
    if scope == "function" and func_name and converted != prompt_code:
        try:
            tree = ast.parse(original_code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
                    lines = original_code.splitlines()
                    new_lines = lines[:node.lineno - 1] + converted.splitlines() + lines[node.end_lineno:]
                    final_code = "\n".join(new_lines)
                    break
        except Exception:
            final_code = original_code
    else:
        final_code = converted

    return final_code, tests


def generate_docstrings(
    original_code: str,
    target_style: str,
    model: str = "meta-llama/llama-4-scout-17b-16e-instruct",
    filename: str = "module.py"
) -> tuple:
    """Generate missing docstrings for all functions in a file.

    Returns:
        tuple: (full_file_code, generated_tests)
    """
    module_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
    sys_prompt = _build_system_prompt(target_style, module_name=module_name)
    user_prompt = f"""Add comprehensive {target_style}-style docstrings to ALL functions and methods that are missing them.
Do NOT remove or change existing code logic.

CODE:
```python
{original_code}
```

Return the COMPLETE file in a single code block."""

    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.05,
        max_tokens=MAX_OUTPUT_TOKENS,
    )

    raw = response.choices[0].message.content.strip()
    return _extract_blocks(raw, original_code)
