import ast
import re
import tempfile
import subprocess
import os
import copy
from functools import lru_cache
from typing import List, Dict, Any
from core import convert_docstring_style

# Cosmetic pydocstyle codes that are always ignored (standard behaviour)
_IGNORED_CODES = {
    "D201",  # blank line before docstring
    "D202",  # blank line after docstring
    "D203",  # 1 blank line before class docstring (conflicts with D211)
    "D205",  # blank line between summary and description
    "D213",  # multi-line summary at second line
    "D400",  # first line should end with period
    "D401",  # first line should be imperative mood
    "D412",  # no blank lines between section header and content
    "D413",  # missing blank line after last section
}

def get_pydocstyle_errors(temp_path: str, style: str = "Google") -> List[Dict[str, Any]]:
    """Run pydocstyle and extract ALL errors per function, keyed by function name."""
    errors = []
    cmd = ["pydocstyle", temp_path]
    if style == "NumPy":
        cmd.append("--convention=numpy")
        
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        lines = result.stdout.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            if temp_path in line and any(k in line for k in (
                " in public function ",
                " in public nested function ",
                " in magic method ",
                " in public method "
            )):
                name_match = re.search(r"[`'\"](\w+)[`'\"]", line)
                func_name = name_match.group(1) if name_match else None

                # Read ALL consecutive error lines for this function block
                i += 1
                while i < len(lines):
                    err_text = lines[i].strip()
                    if temp_path in lines[i]:
                        break
                    if not err_text:
                        break
                    if re.match(r'^[A-Z]\d+:', err_text):
                        code, msg = err_text.split(":", 1)
                        errors.append({
                            "code":      code.strip(),
                            "func_name": func_name,
                            "message":   msg.strip()
                        })
                    i += 1
                continue
            i += 1
    except Exception:
        pass
    return errors


def get_darglint_errors(temp_path: str, style: str = "Google") -> List[Dict[str, Any]]:
    """Run darglint to validate docstring parameter documentation."""
    errors = []
    
    style_map = {
        "Google": "google",
        "reST": "sphinx",
        "NumPy": "numpy",
        "Mixed": "google",
        "None/Incomplete": "google"
    }
    cli_style = style_map.get(style, "google")
    
    try:
        result = subprocess.run(
            ["darglint", "-v", "2", "-s", cli_style, temp_path],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line or line.startswith("Exception"):
                continue
            parts = line.split(":", 4)
            if len(parts) >= 5 and parts[0] == temp_path:
                try:
                    line_no = int(parts[2])
                    code    = parts[3].strip()
                    msg     = parts[4].strip()
                    errors.append({"code": code, "line": line_no, "message": msg})
                except ValueError:
                    pass
    except Exception:
        pass
    return errors


def _get_raw_docstring(node) -> str:
    """Return raw unstripped docstring from AST node.

    ast.get_docstring() strips leading whitespace — hiding missing summary lines.
    We need the raw value to correctly detect D200.
    """
    if (node.body and
            isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
        return node.body[0].value.value
    return ""


def get_ast_errors(file_content: str, functions: list, style: str = "Google") -> None:
    """Catch missing params/returns that darglint misses, using style-specific heuristics."""
    try:
        tree = ast.parse(file_content)
    except SyntaxError:
        return

    func_nodes = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_nodes[node.lineno] = node

    # Style-specific markers
    if style == "reST":
        args_marker = ":param"
        rets_marker = ":return"
        raise_marker = ":raises"
    elif style == "NumPy":
        args_marker = "Parameters"
        rets_marker = "Returns"
        raise_marker = "Raises"
    else:
        # Default Google/Mixed
        args_marker = "Args:"
        rets_marker = "Returns:"
        raise_marker = "Raises:"

    for func in functions:
        node = func_nodes.get(func["start_line"])
        if not node or not func["has_docstring"]:
            continue

        doc            = func["docstring"] or ""
        raw_doc        = _get_raw_docstring(node)
        existing_codes = {e["code"] for e in func["docstring_errors"]}

        # Check 1: No summary line (D200)
        raw_first_line = raw_doc.split("\n")[0]
        if not raw_first_line.strip() and "D200" not in existing_codes:
            func["docstring_errors"].append({
                "code": "D200", "line": func["start_line"],
                "message": "Docstring has no summary line"
            })

        # Check 2: Missing Args
        args = [a.arg for a in node.args.args if a.arg not in ("self", "cls")]
        if args and "DAR101" not in existing_codes:
            if args_marker not in doc:
                func["docstring_errors"].append({
                    "code": "DAR101", "line": func["start_line"],
                    "message": f"Missing '{args_marker}' section — undocumented params: {args}"
                })
            else:
                for arg in args:
                    if arg not in doc:
                        func["docstring_errors"].append({
                            "code": "DAR101", "line": func["start_line"],
                            "message": f"Parameter '{arg}' not documented"
                        })

        # Check 3: Missing Returns
        has_return = any(
            isinstance(n, ast.Return) and n.value is not None
            for n in ast.walk(node)
        )
        if has_return and rets_marker not in doc and "DAR201" not in existing_codes:
            func["docstring_errors"].append({
                "code": "DAR201", "line": func["start_line"],
                "message": f"Missing '{rets_marker}' section in docstring"
            })

        # Check 4: Missing Raises
        raises = [n for n in ast.walk(node) if isinstance(n, ast.Raise) and n.exc is not None]
        if raises and raise_marker not in doc and "DAR401" not in existing_codes:
            func["docstring_errors"].append({
                "code": "DAR401", "line": func["start_line"],
                "message": f"Missing '{raise_marker}' section — function raises exceptions"
            })


def parse_file(file_content: str) -> Dict[str, Any]:
    """Parse a Python file and extract function docstring details.

    Uses an in-process cache keyed by full file content so repeated reruns
    don't repeatedly invoke external linters for unchanged code.
    """
    return copy.deepcopy(_parse_file_cached(file_content))

class FunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
        self.current_class = None

    def visit_ClassDef(self, node):
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node):
        self._save_func(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self._save_func(node)
        self.generic_visit(node)

    def _save_func(self, node):
        docstring = ast.get_docstring(node)
        self.functions.append({
            "name":             node.name,
            "class_name":       self.current_class,
            "start_line":       node.lineno,
            "end_line":         getattr(node, "end_lineno", node.lineno),
            "has_docstring":    docstring is not None,
            "docstring":        docstring,
            "docstring_errors": []
        })

def _parse_file_core(tree, file_content: str) -> Dict[str, Any]:
    visitor = FunctionVisitor()
    visitor.visit(tree)
    functions = visitor.functions

    functions.sort(key=lambda x: x["start_line"])
    func_by_name = {f["name"]: f for f in functions}

    file_style = convert_docstring_style.detect_style(file_content)

    with tempfile.NamedTemporaryFile(
        suffix=".py", delete=False, mode="w", encoding="utf-8"
    ) as f:
        f.write(file_content)
        temp_path = f.name

    try:
        pydoc_errors = get_pydocstyle_errors(temp_path, style=file_style)
        darg_errors  = get_darglint_errors(temp_path, style=file_style)
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass

    # Map pydocstyle errors by function name
    for err in pydoc_errors:
        fname = err.get("func_name")
        if fname and fname in func_by_name:
            func = func_by_name[fname]
            func["docstring_errors"].append({
                "code":    err["code"],
                "line":    func["start_line"],
                "message": err["message"]
            })

    # Map darglint errors by exact def-line match
    for err in darg_errors:
        for func in functions:
            if func["start_line"] == err["line"]:
                func["docstring_errors"].append(err)
                break

    # AST safety net
    get_ast_errors(file_content, functions, style=file_style)

    # Apply standard cosmetic-rule filter
    for func in functions:
        func["docstring_errors"] = [
            e for e in func["docstring_errors"]
            if e["code"] not in _IGNORED_CODES
        ]

    total_functions      = len(functions)
    documented_functions = sum(1 for f in functions if f["has_docstring"])
    total_doc_errors     = sum(len(f["docstring_errors"]) for f in functions)
    coverage             = (documented_functions / total_functions * 100) if total_functions > 0 else 100.0

    return {
        "total_functions":        total_functions,
        "functions":              functions,
        "coverage":               coverage,
        "total_docstring_errors": total_doc_errors,
        "detected_style":         file_style
    }


# Keep compatibility with previous call-sites by routing through core function.
@lru_cache(maxsize=256)
def _parse_file_cached(file_content: str) -> Dict[str, Any]:
    try:
        tree = ast.parse(file_content)
    except SyntaxError:
        return {"error": "Syntax Error: Could not parse file"}
    return _parse_file_core(tree, file_content)