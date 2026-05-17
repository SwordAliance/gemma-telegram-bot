"""Это самый ChatGPT-подобный файл, потому что здесь живут действия, которые модель может инициировать."""
from __future__ import annotations

import ast
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


class SafeExpressionError(ValueError):
    pass


def safe_calc(expression: str) -> str:
    """
    Evaluate a mathematical expression using a restricted AST.
    Allowed: numbers, + - * / // % **, parentheses, unary +/-.
    """
    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.FloorDiv,
        ast.Mod,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Load,
        ast.Pow,
        ast.Call,
        ast.Name,
    )

    tree = ast.parse(expression, mode="eval")

    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            raise SafeExpressionError(f"Disallowed expression element: {type(node).__name__}")
        if isinstance(node, ast.Call) or isinstance(node, ast.Name):
            raise SafeExpressionError("Function calls and names are not allowed.")

    result = eval(compile(tree, "<safe_calc>", "eval"), {"__builtins__": {}}, {})
    return str(result)


def current_time(utc: bool = True) -> str:
    now = datetime.now(timezone.utc if utc else None)
    return now.isoformat()


def format_knowledge_results(results: list[dict[str, str]]) -> str:
    if not results:
        return "Ничего релевантного не найдено."
    lines = []
    for i, item in enumerate(results, start=1):
        lines.append(f"[{i}] Источник: {item['source']}\n{item['text']}")
    return "\n\n".join(lines)


TOOL_SCHEMA = [
    {
        "name": "calculator",
        "description": "Вычисляет арифметическое выражение.",
        "parameters": {"expression": "string"},
    },
    {
        "name": "current_time",
        "description": "Возвращает текущее UTC-время в ISO формате.",
        "parameters": {"utc": "boolean"},
    },
    {
        "name": "search_knowledge",
        "description": "Ищет релевантные фрагменты в локальной базе знаний.",
        "parameters": {"query": "string"},
    },
]


def execute_tool(name: str, args: dict[str, Any], rag_search_fn=None) -> str:
    if name == "calculator":
        expression = str(args.get("expression", ""))
        return safe_calc(expression)

    if name == "current_time":
        utc = bool(args.get("utc", True))
        return current_time(utc=utc)

    if name == "search_knowledge":
        if rag_search_fn is None:
            return "RAG search is unavailable."
        query = str(args.get("query", ""))
        return rag_search_fn(query)

    return f"Unknown tool: {name}"
