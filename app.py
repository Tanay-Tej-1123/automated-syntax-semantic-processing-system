"""
Flask Web Application for Automated Syntax and Semantic Analysis System
Mini-project for Compiler Design Course
"""

import os
from flask import Flask, render_template, request, jsonify
from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from samples import SAMPLE_PROGRAMS, get_samples_dict

app = Flask(__name__)


def count_ast_nodes(node_dict: dict) -> int:
    """Helper to count total nodes in AST."""
    if not node_dict:
        return 0
    count = 1
    for child in node_dict.get("children", []):
        count += count_ast_nodes(child)
    return count


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/samples", methods=["GET"])
def get_samples():
    """Return all preset sample programs."""
    return jsonify({
        "status": "success",
        "samples": SAMPLE_PROGRAMS
    })


@app.route("/api/grammar", methods=["GET"])
def get_grammar():
    """Return formal grammar details and compiler phase information."""
    return jsonify({
        "language_name": "MiniLang",
        "version": "1.0",
        "types": ["int", "float", "bool", "string"],
        "keywords": ["int", "float", "bool", "string", "if", "else", "while", "print", "true", "false"],
        "operators": {
            "arithmetic": ["+", "-", "*", "/", "%"],
            "relational": ["<", "<=", ">", ">="],
            "equality": ["==", "!="],
            "logical": ["&&", "||", "!"],
            "assignment": ["="]
        },
        "delimiters": ["(", ")", "{", "}", ";", ","],
        "ebnf": """Program         ::= Statement* EOF
Statement       ::= VarDecl | Assignment | IfStatement | WhileStatement | PrintStatement | BlockStatement
VarDecl         ::= Type IDENTIFIER ('=' Expression)? ';'
Type            ::= 'int' | 'float' | 'bool' | 'string'
Assignment      ::= IDENTIFIER '=' Expression ';'
IfStatement     ::= 'if' '(' Expression ')' Statement ('else' Statement)?
WhileStatement  ::= 'while' '(' Expression ')' Statement
PrintStatement  ::= 'print' '(' Expression ')' ';'
BlockStatement  ::= '{' Statement* '}'
Expression      ::= LogicalOr
LogicalOr       ::= LogicalAnd ( '||' LogicalAnd )*
LogicalAnd      ::= Equality ( '&&' Equality )*
Equality        ::= Relational ( ('==' | '!=') Relational )*
Relational      ::= Additive ( ('<' | '<=' | '>' | '>=') Additive )*
Additive        ::= Multiplicative ( ('+' | '-') Multiplicative )*
Multiplicative  ::= Unary ( ('*' | '/' | '%') Unary )*
Unary           ::= ('!' | '-' | '+') Unary | Primary
Primary         ::= INT_LIT | FLOAT_LIT | STRING_LIT | BOOL_LIT | IDENTIFIER | '(' Expression ')'"""
    })


@app.route("/api/analyze", methods=["POST"])
def analyze_code():
    """
    Main Compiler Pipeline Endpoint:
    1. Lexical Analysis
    2. Syntax Analysis
    3. Semantic Analysis & Symbol Table Generation
    """
    data = request.get_json(silent=True) or {}
    source_code = data.get("code", "")

    if not source_code.strip():
        return jsonify({
            "status": "EMPTY_CODE",
            "message": "Source code is empty. Please enter code or load a sample program."
        })

    # Step 1: Lexical Analysis
    lexer = Lexer(source_code)
    tokens, lex_errors = lexer.tokenize()

    tokens_serialized = [t.to_dict() for t in tokens]
    lex_errors_serialized = [e.to_dict() for e in lex_errors]

    # Step 2: Syntax Analysis
    parser = Parser(tokens)
    ast, syn_errors, derivation_steps = parser.parse()
    syn_errors_serialized = [e.to_dict() for e in syn_errors]

    # Step 3: Semantic Analysis
    sem_errors_serialized = []
    warnings_serialized = []
    symbol_table_serialized = []

    if ast is not None:
        analyzer = SemanticAnalyzer()
        symbols, sem_errors, warnings = analyzer.analyze(ast)
        symbol_table_serialized = symbols
        sem_errors_serialized = [e.to_dict() for e in sem_errors]
        warnings_serialized = [w.to_dict() for w in warnings]

    # Total Error Counting
    total_errors = len(lex_errors_serialized) + len(syn_errors_serialized) + len(sem_errors_serialized)
    ast_serialized = ast.to_dict() if ast is not None else None
    ast_node_count = count_ast_nodes(ast_serialized) if ast_serialized else 0

    phase_status = {
        "lexical": "PASSED" if len(lex_errors_serialized) == 0 else "FAILED",
        "syntax": "PASSED" if len(syn_errors_serialized) == 0 else "FAILED",
        "semantic": "PASSED" if len(sem_errors_serialized) == 0 else "FAILED"
    }

    final_status = "SUCCESS" if total_errors == 0 else "ERRORS_DETECTED"

    return jsonify({
        "status": final_status,
        "summary": {
            "total_lines": len(source_code.splitlines()),
            "token_count": len([t for t in tokens if t.type.name != "EOF"]),
            "ast_node_count": ast_node_count,
            "symbol_count": len(symbol_table_serialized),
            "lexical_errors_count": len(lex_errors_serialized),
            "syntax_errors_count": len(syn_errors_serialized),
            "semantic_errors_count": len(sem_errors_serialized),
            "warnings_count": len(warnings_serialized),
            "total_errors": total_errors
        },
        "phase_status": phase_status,
        "tokens": tokens_serialized,
        "lexical_errors": lex_errors_serialized,
        "syntax_errors": syn_errors_serialized,
        "semantic_errors": sem_errors_serialized,
        "warnings": warnings_serialized,
        "derivation_steps": derivation_steps,
        "symbol_table": symbol_table_serialized,
        "ast": ast_serialized
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
