import ast
import re
import sys
import os
from datasets import load_dataset

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'graph'))
from db import get_db

def extract_functions_from_code(source_code):
    def _walk_ast(tree):
        return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

    try:
        return _walk_ast(ast.parse(source_code))
    except SyntaxError:
        pass

    try:
        indented = "\n".join("    " + line for line in source_code.splitlines())
        return _walk_ast(ast.parse(f"def _wrapper():\n{indented}"))
    except SyntaxError:
        pass

    return re.findall(r"^\s*def\s+([a-zA-Z_]\w*)\s*\(", source_code, re.MULTILINE)

def load_cvefixes(limit=5000):
    print("loading CVEfixes dataset from HuggingFace...")
    dataset = load_dataset("hitoshura25/cvefixes", split="train")

    db = get_db()
    collection = db["labeled_functions"]

    inserted = 0
    skipped = 0

    for record in dataset:
        if inserted >= limit:
            break

        # field is 'language' not 'programming_language'
        lang = record.get("language", "")
        if lang.lower() != "python":
            skipped += 1
            continue

        vulnerable_code = record.get("vulnerable_code", "")
        fixed_code = record.get("fixed_code", "")

        if not vulnerable_code or not fixed_code:
            skipped += 1
            continue

        vuln_functions = extract_functions_from_code(vulnerable_code)
        for func_name in vuln_functions:
            collection.insert_one({
                "func_name": func_name,
                "source": "cvefixes",
                "label": 1,
                "code": vulnerable_code,
                "repo": record.get("repo_url", "unknown")
            })
            inserted += 1

        fixed_functions = extract_functions_from_code(fixed_code)
        for func_name in fixed_functions:
            collection.insert_one({
                "func_name": func_name,
                "source": "cvefixes",
                "label": 0,
                "code": fixed_code,
                "repo": record.get("repo_url", "unknown")
            })

    print(f"inserted {inserted} vulnerable functions")
    print(f"skipped {skipped} non-Python records")

if __name__ == "__main__":
    load_cvefixes(limit=5000)