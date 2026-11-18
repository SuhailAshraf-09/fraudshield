import ast
from pathlib import Path
from app import database

print("\nFRAUDSHIELD AI - BACKEND DATABASE INSPECTION")

file = Path("app/database.py")

if not file.exists():
    raise SystemExit("Database configuration file missing.")

tree = ast.parse(file.read_text(encoding="utf-8-sig"))

print("Current Engine:", database.engine.dialect.name)
print("SQLAlchemy Base:", hasattr(database, "Base"))
print("SessionLocal:", hasattr(database, "SessionLocal"))
print("get_db:", hasattr(database, "get_db"))

print("\nDATABASE MODULE STRUCTURE")

for node in tree.body:
    if isinstance(node, ast.Assign):
        names = [
            t.id
            for t in node.targets
            if isinstance(t, ast.Name)
        ]
        if names:
            print("Variable:", ", ".join(names))

    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        print("Function:", node.name)

print("\nBACKEND DATABASE IMPORTS")

for path in sorted(Path("app").rglob("*.py")):
    try:
        module = ast.parse(
            path.read_text(encoding="utf-8-sig")
        )
    except (SyntaxError, UnicodeError):
        continue

    for node in ast.walk(module):
        if isinstance(node, ast.ImportFrom):
            if node.module in ("app.database", "database"):
                names = [a.name for a in node.names]
                print(path, "imports", ", ".join(names))

print("\nINSPECTION COMPLETED")
print("No database files or records modified.")
print("No passwords displayed.")
