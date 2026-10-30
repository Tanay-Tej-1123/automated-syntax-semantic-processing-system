"""
Abstract Syntax Tree (AST) Node Definitions for MiniLang
Automated Syntax and Semantic Analysis System
"""

from typing import List, Optional, Any, Dict


class ASTNode:
    """Base class for all AST nodes."""
    def __init__(self, line: int, column: int):
        self.line = line
        self.column = column

    def to_dict(self) -> Dict[str, Any]:
        """Convert AST node to nested dictionary for JSON serialization & visual tree."""
        raise NotImplementedError("Subclasses must implement to_dict()")


class ProgramNode(ASTNode):
    def __init__(self, statements: List[ASTNode], line: int = 1, column: int = 1):
        super().__init__(line, column)
        self.statements = statements

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "Program",
            "label": "Program",
            "line": self.line,
            "column": self.column,
            "children": [stmt.to_dict() for stmt in self.statements]
        }


class VarDeclNode(ASTNode):
    def __init__(self, var_type: str, var_name: str, init_expr: Optional[ASTNode], line: int, column: int):
        super().__init__(line, column)
        self.var_type = var_type
        self.var_name = var_name
        self.init_expr = init_expr

    def to_dict(self) -> Dict[str, Any]:
        children = []
        if self.init_expr:
            children.append(self.init_expr.to_dict())
        return {
            "node_type": "VarDecl",
            "label": f"VarDecl: {self.var_type} {self.var_name}",
            "var_type": self.var_type,
            "var_name": self.var_name,
            "has_initializer": self.init_expr is not None,
            "line": self.line,
            "column": self.column,
            "children": children
        }


class AssignmentNode(ASTNode):
    def __init__(self, var_name: str, expr: ASTNode, line: int, column: int):
        super().__init__(line, column)
        self.var_name = var_name
        self.expr = expr

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "Assignment",
            "label": f"Assign: {self.var_name} =",
            "var_name": self.var_name,
            "line": self.line,
            "column": self.column,
            "children": [self.expr.to_dict()]
        }


class IfNode(ASTNode):
    def __init__(self, condition: ASTNode, then_branch: ASTNode, else_branch: Optional[ASTNode], line: int, column: int):
        super().__init__(line, column)
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def to_dict(self) -> Dict[str, Any]:
        children = [
            {"node_type": "Condition", "label": "Condition", "children": [self.condition.to_dict()]},
            {"node_type": "ThenBranch", "label": "Then Branch", "children": [self.then_branch.to_dict()]},
        ]
        if self.else_branch:
            children.append({"node_type": "ElseBranch", "label": "Else Branch", "children": [self.else_branch.to_dict()]})
        return {
            "node_type": "IfStatement",
            "label": "If Statement",
            "line": self.line,
            "column": self.column,
            "children": children
        }


class WhileNode(ASTNode):
    def __init__(self, condition: ASTNode, body: ASTNode, line: int, column: int):
        super().__init__(line, column)
        self.condition = condition
        self.body = body

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "WhileStatement",
            "label": "While Statement",
            "line": self.line,
            "column": self.column,
            "children": [
                {"node_type": "Condition", "label": "Loop Condition", "children": [self.condition.to_dict()]},
                {"node_type": "Body", "label": "Loop Body", "children": [self.body.to_dict()]}
            ]
        }


class PrintNode(ASTNode):
    def __init__(self, expr: ASTNode, line: int, column: int):
        super().__init__(line, column)
        self.expr = expr

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "PrintStatement",
            "label": "Print Statement",
            "line": self.line,
            "column": self.column,
            "children": [self.expr.to_dict()]
        }


class BlockNode(ASTNode):
    def __init__(self, statements: List[ASTNode], line: int, column: int):
        super().__init__(line, column)
        self.statements = statements

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "Block",
            "label": "Block { ... }",
            "line": self.line,
            "column": self.column,
            "children": [stmt.to_dict() for stmt in self.statements]
        }


class BinaryOpNode(ASTNode):
    def __init__(self, left: ASTNode, op: str, right: ASTNode, line: int, column: int):
        super().__init__(line, column)
        self.left = left
        self.op = op
        self.right = right

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "BinaryOp",
            "label": f"BinaryOp ({self.op})",
            "op": self.op,
            "line": self.line,
            "column": self.column,
            "children": [self.left.to_dict(), self.right.to_dict()]
        }


class UnaryOpNode(ASTNode):
    def __init__(self, op: str, operand: ASTNode, line: int, column: int):
        super().__init__(line, column)
        self.op = op
        self.operand = operand

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "UnaryOp",
            "label": f"UnaryOp ({self.op})",
            "op": self.op,
            "line": self.line,
            "column": self.column,
            "children": [self.operand.to_dict()]
        }


class LiteralNode(ASTNode):
    def __init__(self, lit_type: str, value: Any, line: int, column: int):
        super().__init__(line, column)
        self.lit_type = lit_type
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        val_display = f'"{self.value}"' if self.lit_type == "string" else str(self.value)
        return {
            "node_type": "Literal",
            "label": f"Literal: {val_display} ({self.lit_type})",
            "lit_type": self.lit_type,
            "value": self.value,
            "line": self.line,
            "column": self.column,
            "children": []
        }


class IdentifierNode(ASTNode):
    def __init__(self, name: str, line: int, column: int):
        super().__init__(line, column)
        self.name = name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "Identifier",
            "label": f"Identifier: {self.name}",
            "name": self.name,
            "line": self.line,
            "column": self.column,
            "children": []
        }
