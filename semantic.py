"""
Semantic Analyzer and Scoped Symbol Table for MiniLang
Automated Syntax and Semantic Analysis System
"""

from typing import List, Dict, Optional, Any, Tuple
from ast_nodes import (
    ASTNode, ProgramNode, VarDeclNode, AssignmentNode, IfNode, WhileNode,
    PrintNode, BlockNode, BinaryOpNode, UnaryOpNode, LiteralNode, IdentifierNode
)


class Symbol:
    """Represents a variable symbol inside a scope."""
    def __init__(self, name: str, var_type: str, scope_level: int, scope_name: str,
                 line: int, column: int, initialized: bool = False, value_preview: Optional[str] = None):
        self.name = name
        self.type = var_type
        self.scope_level = scope_level
        self.scope_name = scope_name
        self.line = line
        self.column = column
        self.initialized = initialized
        self.value_preview = value_preview

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "scope_level": self.scope_level,
            "scope_name": self.scope_name,
            "line": self.line,
            "column": self.column,
            "initialized": "Yes" if self.initialized else "No",
            "value_preview": str(self.value_preview) if self.value_preview is not None else "-"
        }

    def __repr__(self) -> str:
        return f"Symbol({self.name}: {self.type}, Scope: {self.scope_name}, Init: {self.initialized})"


class SymbolTable:
    """Scoped Symbol Table supporting nested lexical scopes."""
    def __init__(self, scope_name: str = "Global", scope_level: int = 0, parent: Optional['SymbolTable'] = None):
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        self.all_recorded_symbols: List[Symbol] = []  # Keeps history across scope exits for visual reporting

    def lookup_current(self, name: str) -> Optional[Symbol]:
        """Look up identifier strictly in current scope."""
        return self.symbols.get(name)

    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up identifier in current scope and bubble up to parent scopes."""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        return None

    def insert(self, symbol: Symbol) -> bool:
        """Insert a symbol into the current scope. Returns False if already declared."""
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        self.all_recorded_symbols.append(symbol)
        return True


class SemanticErrorRecord:
    def __init__(self, error_type: str, message: str, line: int, column: int):
        self.error_type = error_type
        self.message = message
        self.line = line
        self.column = column

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": "Semantic",
            "error_type": self.error_type,
            "message": self.message,
            "line": self.line,
            "column": self.column
        }

    def __repr__(self) -> str:
        return f"SemanticError({self.error_type}: {self.message} at Line {self.line}:{self.column})"


class SemanticWarningRecord:
    def __init__(self, warning_type: str, message: str, line: int, column: int):
        self.warning_type = warning_type
        self.message = message
        self.line = line
        self.column = column

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": "Semantic Warning",
            "warning_type": self.warning_type,
            "message": self.message,
            "line": self.line,
            "column": self.column
        }


class SemanticAnalyzer:
    """
    Semantic Analyzer for MiniLang.
    Performs scope validation, type checking, duplicate detection, and symbol table generation.
    """

    def __init__(self):
        self.global_scope = SymbolTable("Global", 0, None)
        self.current_scope = self.global_scope
        self.errors: List[SemanticErrorRecord] = []
        self.warnings: List[SemanticWarningRecord] = []
        self.collected_symbols: List[Symbol] = []
        self.scope_counter = 0

    def analyze(self, ast: Optional[ProgramNode]) -> Tuple[List[Dict[str, Any]], List[SemanticErrorRecord], List[SemanticWarningRecord]]:
        """Run semantic analysis on the provided AST."""
        self.global_scope = SymbolTable("Global", 0, None)
        self.current_scope = self.global_scope
        self.errors = []
        self.warnings = []
        self.collected_symbols = []
        self.scope_counter = 0

        if ast is None:
            return [], self.errors, self.warnings

        self.visit(ast)

        # Collect symbols for display
        table_records = [sym.to_dict() for sym in self.collected_symbols]
        return table_records, self.errors, self.warnings

    def _enter_scope(self, name_prefix: str = "Block") -> SymbolTable:
        self.scope_counter += 1
        scope_name = f"{name_prefix} (Level {self.current_scope.scope_level + 1})"
        new_scope = SymbolTable(scope_name, self.current_scope.scope_level + 1, self.current_scope)
        self.current_scope = new_scope
        return new_scope

    def _exit_scope(self):
        if self.current_scope.parent is not None:
            self.current_scope = self.current_scope.parent

    # ---------------- Visitor Dispatch ----------------

    def visit(self, node: ASTNode) -> Optional[str]:
        """Dispatch visit based on node type. Returns expression type for expr nodes."""
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode):
        raise NotImplementedError(f"No visit_{type(node).__name__} method defined in SemanticAnalyzer.")

    # ---------------- Statement Visitors ----------------

    def visit_ProgramNode(self, node: ProgramNode):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_VarDeclNode(self, node: VarDeclNode):
        # 1. Check for Duplicate Declaration in current scope
        existing = self.current_scope.lookup_current(node.var_name)
        if existing:
            self.errors.append(
                SemanticErrorRecord(
                    "DuplicateDeclaration",
                    f"Variable '{node.var_name}' is already declared in scope '{self.current_scope.scope_name}' (previously at Line {existing.line}, Col {existing.column})",
                    node.line,
                    node.column
                )
            )
            return

        initialized = False
        val_preview = None

        # 2. Check Initializer Expression Type
        if node.init_expr is not None:
            expr_type = self.visit(node.init_expr)
            if expr_type is not None:
                if not self._is_type_compatible(node.var_type, expr_type):
                    self.errors.append(
                        SemanticErrorRecord(
                            "TypeMismatch",
                            f"Cannot initialize variable '{node.var_name}' of type '{node.var_type}' with expression of incompatible type '{expr_type}'",
                            node.line,
                            node.column
                        )
                    )
                initialized = True
                if isinstance(node.init_expr, LiteralNode):
                    val_preview = f'"{node.init_expr.value}"' if node.init_expr.lit_type == "string" else str(node.init_expr.value)

        # 3. Insert into current scope
        sym = Symbol(
            name=node.var_name,
            var_type=node.var_type,
            scope_level=self.current_scope.scope_level,
            scope_name=self.current_scope.scope_name,
            line=node.line,
            column=node.column,
            initialized=initialized,
            value_preview=val_preview
        )
        self.current_scope.insert(sym)
        self.collected_symbols.append(sym)

    def visit_AssignmentNode(self, node: AssignmentNode):
        # 1. Check if variable was declared
        sym = self.current_scope.lookup(node.var_name)
        if sym is None:
            self.errors.append(
                SemanticErrorRecord(
                    "UndeclaredVariable",
                    f"Variable '{node.var_name}' is assigned before declaration. Did you forget to declare it with 'int', 'float', 'bool', or 'string'?",
                    node.line,
                    node.column
                )
            )
            # Still visit the expr to find other errors
            self.visit(node.expr)
            return

        # 2. Type Check Assignment
        expr_type = self.visit(node.expr)
        if expr_type is not None:
            if not self._is_type_compatible(sym.type, expr_type):
                self.errors.append(
                    SemanticErrorRecord(
                        "TypeMismatch",
                        f"Cannot assign value of type '{expr_type}' to variable '{node.var_name}' of type '{sym.type}'",
                        node.line,
                        node.column
                    )
                )

        sym.initialized = True
        if isinstance(node.expr, LiteralNode):
            sym.value_preview = f'"{node.expr.value}"' if node.expr.lit_type == "string" else str(node.expr.value)

    def visit_IfNode(self, node: IfNode):
        cond_type = self.visit(node.condition)
        if cond_type is not None and cond_type != "bool":
            self.errors.append(
                SemanticErrorRecord(
                    "ConditionTypeError",
                    f"Condition in 'if' statement must evaluate to 'bool', but found type '{cond_type}'",
                    node.line,
                    node.column
                )
            )

        self.visit(node.then_branch)
        if node.else_branch:
            self.visit(node.else_branch)

    def visit_WhileNode(self, node: WhileNode):
        cond_type = self.visit(node.condition)
        if cond_type is not None and cond_type != "bool":
            self.errors.append(
                SemanticErrorRecord(
                    "ConditionTypeError",
                    f"Condition in 'while' statement must evaluate to 'bool', but found type '{cond_type}'",
                    node.line,
                    node.column
                )
            )

        self.visit(node.body)

    def visit_PrintNode(self, node: PrintNode):
        self.visit(node.expr)

    def visit_BlockNode(self, node: BlockNode):
        self._enter_scope("Block")
        for stmt in node.statements:
            self.visit(stmt)
        self._exit_scope()

    # ---------------- Expression Visitors ----------------

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> Optional[str]:
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if left_type is None or right_type is None:
            return None

        op = node.op

        # 1. Arithmetic Operators (+, -, *, /, %)
        if op in ("+", "-", "*", "/", "%"):
            # String concatenation via '+'
            if op == "+" and (left_type == "string" or right_type == "string"):
                return "string"

            # Check division / modulo by zero literal
            if op in ("/", "%") and isinstance(node.right, LiteralNode):
                if node.right.value == 0 or node.right.value == 0.0:
                    self.errors.append(
                        SemanticErrorRecord(
                            "DivisionByZero",
                            f"Division or modulo by zero constant detected in expression with operator '{op}'",
                            node.line,
                            node.column
                        )
                    )

            # Both operands must be numeric
            if not self._is_numeric(left_type) or not self._is_numeric(right_type):
                self.errors.append(
                    SemanticErrorRecord(
                        "TypeMismatch",
                        f"Operator '{op}' is not supported between types '{left_type}' and '{right_type}'. Operands must be numeric (int/float)",
                        node.line,
                        node.column
                    )
                )
                return "int"

            # Modulo operator requires integers
            if op == "%" and (left_type != "int" or right_type != "int"):
                self.errors.append(
                    SemanticErrorRecord(
                        "TypeMismatch",
                        f"Modulo operator '%' requires integer operands, but found '{left_type}' and '{right_type}'",
                        node.line,
                        node.column
                    )
                )
                return "int"

            # Division yields float if either is float or standard float division
            if op == "/" or left_type == "float" or right_type == "float":
                return "float"
            return "int"

        # 2. Relational Operators (<, <=, >, >=)
        if op in ("<", "<=", ">", ">="):
            if not self._is_numeric(left_type) or not self._is_numeric(right_type):
                self.errors.append(
                    SemanticErrorRecord(
                        "TypeMismatch",
                        f"Relational comparison '{op}' requires numeric operands, but found '{left_type}' and '{right_type}'",
                        node.line,
                        node.column
                    )
                )
            return "bool"

        # 3. Equality Operators (==, !=)
        if op in ("==", "!="):
            if self._is_numeric(left_type) and self._is_numeric(right_type):
                return "bool"
            if left_type != right_type:
                self.errors.append(
                    SemanticErrorRecord(
                        "TypeMismatch",
                        f"Equality comparison '{op}' between incompatible types '{left_type}' and '{right_type}'",
                        node.line,
                        node.column
                    )
                )
            return "bool"

        # 4. Logical Operators (&&, ||)
        if op in ("&&", "||"):
            if left_type != "bool" or right_type != "bool":
                self.errors.append(
                    SemanticErrorRecord(
                        "TypeMismatch",
                        f"Logical operator '{op}' requires boolean operands, but found '{left_type}' and '{right_type}'",
                        node.line,
                        node.column
                    )
                )
            return "bool"

        return "unknown"

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> Optional[str]:
        operand_type = self.visit(node.operand)
        if operand_type is None:
            return None

        if node.op == "!":
            if operand_type != "bool":
                self.errors.append(
                    SemanticErrorRecord(
                        "TypeMismatch",
                        f"Logical NOT operator '!' requires boolean operand, but found '{operand_type}'",
                        node.line,
                        node.column
                    )
                )
            return "bool"

        if node.op in ("-", "+"):
            if not self._is_numeric(operand_type):
                self.errors.append(
                    SemanticErrorRecord(
                        "TypeMismatch",
                        f"Unary operator '{node.op}' requires numeric operand, but found '{operand_type}'",
                        node.line,
                        node.column
                    )
                )
            return operand_type

        return operand_type

    def visit_LiteralNode(self, node: LiteralNode) -> str:
        return node.lit_type

    def visit_IdentifierNode(self, node: IdentifierNode) -> Optional[str]:
        sym = self.current_scope.lookup(node.name)
        if sym is None:
            self.errors.append(
                SemanticErrorRecord(
                    "UndeclaredVariable",
                    f"Variable '{node.name}' is referenced before declaration",
                    node.line,
                    node.column
                )
            )
            return None

        if not sym.initialized:
            self.warnings.append(
                SemanticWarningRecord(
                    "UninitializedVariable",
                    f"Variable '{node.name}' may be uninitialized when read",
                    node.line,
                    node.column
                )
            )

        return sym.type

    # ---------------- Type Helpers ----------------

    def _is_numeric(self, t: str) -> bool:
        return t in ("int", "float")

    def _is_type_compatible(self, target_type: str, source_type: str) -> bool:
        """
        Check if source_type can be assigned to target_type.
        Exact match is always valid.
        int can be implicitly promoted to float.
        """
        if target_type == source_type:
            return True
        if target_type == "float" and source_type == "int":
            return True  # Safe implicit widening
        return False
