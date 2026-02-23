import ast
from typing import List, Dict, Any

def parse_file(file_content: str) -> Dict[str, Any]:
    """Parse a python file and extract function details."""
    try:
        tree = ast.parse(file_content)
    except SyntaxError:
        return {"error": "Syntax Error: Could not parse file"}
    
    functions = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            docstring = ast.get_docstring(node)
            functions.append({
                "name": node.name,
                "start_line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno),
                "has_docstring": docstring is not None,
                "docstring": docstring
            })
            
    # Sort functions by start_line
    functions.sort(key=lambda x: x["start_line"])
    
    total_functions = len(functions)
    documented_functions = sum(1 for f in functions if f["has_docstring"])
    
    if total_functions > 0:
        coverage = (documented_functions / total_functions) * 100
    else:
        coverage = 100.0
        
    return {
        "total_functions": total_functions,
        "functions": functions,
        "coverage": coverage
    }
