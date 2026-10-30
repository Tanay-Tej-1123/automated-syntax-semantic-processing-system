"""
Recursive Descent Syntax Analyzer (Parser) for MiniLang
Automated Syntax and Semantic Analysis System
"""

from typing import List, Optional, Tuple, Dict, Any
from lexer import Token, TokenType
from ast_nodes import (
    ASTNode, ProgramNode, VarDeclNode, AssignmentNode, IfNode, WhileNode,
    PrintNode, BlockNode, BinaryOpNode, UnaryOpNode, LiteralNode, IdentifierNode
)


class SyntaxErrorRecord:
    def __init__(self, message: str, line: int, column: int, offending_token: str = ""):
        self.message = message
        self.line = line
        self.column = column
        self.offending_token = offending_token

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": "Syntax",
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "offending_token": self.offending_token
        }

    def __repr__(self) -> str:
        return f"SyntaxError({self.message} at Line {self.line}:{self.column})"


class ParseException(Exception):
    def __init__(self, message: str, token: Token):
        super().__init__(message)
        self.message = message
        self.token = token


class Parser:
    """
    Recursive Descent Parser for MiniLang.
    Builds an Abstract Syntax Tree (AST) and logs grammar derivation rules.
    """

    TYPE_KEYWORDS = {
        TokenType.KEYWORD_INT: "int",
        TokenType.KEYWORD_FLOAT: "float",
        TokenType.KEYWORD_BOOL: "bool",
        TokenType.KEYWORD_STRING: "string"
    }

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.errors: List[SyntaxErrorRecord] = []
        self.derivation_steps: List[str] = []

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _match(self, *token_types: TokenType) -> bool:
        for t_type in token_types:
            if self._check(t_type):
                self._advance()
                return True
        return False

    def _consume(self, token_type: TokenType, error_message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        curr = self._peek()
        raise ParseException(f"{error_message} (Found '{curr.value}' of type {curr.type.name})", curr)

    def _log_rule(self, rule: str):
        self.derivation_steps.append(rule)

    def _synchronize(self):
        """Error recovery: advance past error boundary to next statement."""
        self._advance()
        while not self._is_at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return
            if self._peek().type in (
                TokenType.KEYWORD_INT,
                TokenType.KEYWORD_FLOAT,
                TokenType.KEYWORD_BOOL,
                TokenType.KEYWORD_STRING,
                TokenType.KEYWORD_IF,
                TokenType.KEYWORD_WHILE,
                TokenType.KEYWORD_PRINT,
                TokenType.LBRACE,
                TokenType.RBRACE
            ):
                return
            self._advance()

    def parse(self) -> Tuple[Optional[ProgramNode], List[SyntaxErrorRecord], List[str]]:
        """Entry point for parsing program."""
        self.current = 0
        self.errors = []
        self.derivation_steps = []
        self._log_rule("Program -> Statement* EOF")

        statements: List[ASTNode] = []
        start_line = self._peek().line
        start_col = self._peek().column

        while not self._is_at_end():
            try:
                stmt = self.statement()
                if stmt is not None:
                    statements.append(stmt)
            except ParseException as e:
                self.errors.append(
                    SyntaxErrorRecord(
                        e.message,
                        e.token.line,
                        e.token.column,
                        str(e.token.value)
                    )
                )
                self._synchronize()

        prog_node = ProgramNode(statements, start_line, start_col)
        return prog_node, self.errors, self.derivation_steps

    # ---------------- Statement Rules ----------------

    def statement(self) -> Optional[ASTNode]:
        """
        Statement -> VarDecl | Assignment | IfStatement | WhileStatement | PrintStatement | Block
        """
        curr = self._peek()

        # Variable Declaration: int | float | bool | string
        if curr.type in self.TYPE_KEYWORDS:
            return self.var_declaration()

        # If Statement
        if curr.type == TokenType.KEYWORD_IF:
            return self.if_statement()

        # While Statement
        if curr.type == TokenType.KEYWORD_WHILE:
            return self.while_statement()

        # Print Statement
        if curr.type == TokenType.KEYWORD_PRINT:
            return self.print_statement()

        # Block Statement
        if curr.type == TokenType.LBRACE:
            return self.block_statement()

        # Assignment Statement: IDENTIFIER = Expression ;
        if curr.type == TokenType.IDENTIFIER:
            return self.assignment_statement()

        # Unexpected token
        raise ParseException(f"Unexpected token '{curr.value}' at start of statement", curr)

    def var_declaration(self) -> ASTNode:
        """
        VarDecl -> Type IDENTIFIER ('=' Expression)? ';'
        """
        type_token = self._advance()
        var_type = self.TYPE_KEYWORDS[type_token.type]

        id_token = self._consume(TokenType.IDENTIFIER, f"Expected identifier name after type '{var_type}'")
        var_name = str(id_token.value)

        init_expr = None
        if self._match(TokenType.ASSIGN):
            self._log_rule(f"VarDecl -> {var_type} {var_name} = Expression ;")
            init_expr = self.expression()
        else:
            self._log_rule(f"VarDecl -> {var_type} {var_name} ;")

        self._consume(TokenType.SEMICOLON, f"Missing semicolon ';' after declaration of '{var_name}'")
        return VarDeclNode(var_type, var_name, init_expr, type_token.line, type_token.column)

    def assignment_statement(self) -> ASTNode:
        """
        Assignment -> IDENTIFIER '=' Expression ';'
        """
        id_token = self._advance()
        var_name = str(id_token.value)

        self._consume(TokenType.ASSIGN, f"Expected '=' assignment operator after identifier '{var_name}'")
        self._log_rule(f"Assignment -> {var_name} = Expression ;")
        expr = self.expression()
        self._consume(TokenType.SEMICOLON, f"Missing semicolon ';' after assignment to '{var_name}'")
        return AssignmentNode(var_name, expr, id_token.line, id_token.column)

    def if_statement(self) -> ASTNode:
        """
        IfStatement -> 'if' '(' Expression ')' Statement ('else' Statement)?
        """
        if_token = self._advance()  # consume 'if'
        self._log_rule("IfStatement -> 'if' '(' Expression ')' Statement ('else' Statement)?")

        self._consume(TokenType.LPAREN, "Expected '(' after 'if'")
        condition = self.expression()
        self._consume(TokenType.RPAREN, "Expected ')' after if-condition")

        then_branch = self.statement()
        else_branch = None
        if self._match(TokenType.KEYWORD_ELSE):
            else_branch = self.statement()

        return IfNode(condition, then_branch, else_branch, if_token.line, if_token.column)

    def while_statement(self) -> ASTNode:
        """
        WhileStatement -> 'while' '(' Expression ')' Statement
        """
        while_token = self._advance()  # consume 'while'
        self._log_rule("WhileStatement -> 'while' '(' Expression ')' Statement")

        self._consume(TokenType.LPAREN, "Expected '(' after 'while'")
        condition = self.expression()
        self._consume(TokenType.RPAREN, "Expected ')' after while-condition")

        body = self.statement()
        return WhileNode(condition, body, while_token.line, while_token.column)

    def print_statement(self) -> ASTNode:
        """
        PrintStatement -> 'print' '(' Expression ')' ';'
        """
        print_token = self._advance()  # consume 'print'
        self._log_rule("PrintStatement -> 'print' '(' Expression ')' ;")

        self._consume(TokenType.LPAREN, "Expected '(' after 'print'")
        expr = self.expression()
        self._consume(TokenType.RPAREN, "Expected ')' after print expression")
        self._consume(TokenType.SEMICOLON, "Missing semicolon ';' after print statement")

        return PrintNode(expr, print_token.line, print_token.column)

    def block_statement(self) -> ASTNode:
        """
        BlockStatement -> '{' Statement* '}'
        """
        open_brace = self._advance()  # consume '{'
        self._log_rule("BlockStatement -> '{' Statement* '}'")
        statements: List[ASTNode] = []

        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            try:
                stmt = self.statement()
                if stmt is not None:
                    statements.append(stmt)
            except ParseException as e:
                self.errors.append(
                    SyntaxErrorRecord(e.message, e.token.line, e.token.column, str(e.token.value))
                )
                self._synchronize()

        self._consume(TokenType.RBRACE, "Missing closing brace '}' for block")
        return BlockNode(statements, open_brace.line, open_brace.column)

    # ---------------- Expression Rules (Precedence Climbing) ----------------

    def expression(self) -> ASTNode:
        """Expression -> LogicalOr"""
        return self.logical_or()

    def logical_or(self) -> ASTNode:
        """LogicalOr -> LogicalAnd ( '||' LogicalAnd )*"""
        expr = self.logical_and()
        while self._match(TokenType.OR):
            op_token = self._previous()
            self._log_rule("LogicalOr -> LogicalOr '||' LogicalAnd")
            right = self.logical_and()
            expr = BinaryOpNode(expr, "||", right, op_token.line, op_token.column)
        return expr

    def logical_and(self) -> ASTNode:
        """LogicalAnd -> Equality ( '&&' Equality )*"""
        expr = self.equality()
        while self._match(TokenType.AND):
            op_token = self._previous()
            self._log_rule("LogicalAnd -> LogicalAnd '&&' Equality")
            right = self.equality()
            expr = BinaryOpNode(expr, "&&", right, op_token.line, op_token.column)
        return expr

    def equality(self) -> ASTNode:
        """Equality -> Relational ( ('==' | '!=') Relational )*"""
        expr = self.relational()
        while self._match(TokenType.EQ, TokenType.NEQ):
            op_token = self._previous()
            self._log_rule(f"Equality -> Equality '{op_token.value}' Relational")
            right = self.relational()
            expr = BinaryOpNode(expr, str(op_token.value), right, op_token.line, op_token.column)
        return expr

    def relational(self) -> ASTNode:
        """Relational -> Additive ( ('<' | '<=' | '>' | '>=') Additive )*"""
        expr = self.additive()
        while self._match(TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE):
            op_token = self._previous()
            self._log_rule(f"Relational -> Relational '{op_token.value}' Additive")
            right = self.additive()
            expr = BinaryOpNode(expr, str(op_token.value), right, op_token.line, op_token.column)
        return expr

    def additive(self) -> ASTNode:
        """Additive -> Multiplicative ( ('+' | '-') Multiplicative )*"""
        expr = self.multiplicative()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op_token = self._previous()
            self._log_rule(f"Additive -> Additive '{op_token.value}' Multiplicative")
            right = self.multiplicative()
            expr = BinaryOpNode(expr, str(op_token.value), right, op_token.line, op_token.column)
        return expr

    def multiplicative(self) -> ASTNode:
        """Multiplicative -> Unary ( ('*' | '/' | '%') Unary )*"""
        expr = self.unary()
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op_token = self._previous()
            self._log_rule(f"Multiplicative -> Multiplicative '{op_token.value}' Unary")
            right = self.unary()
            expr = BinaryOpNode(expr, str(op_token.value), right, op_token.line, op_token.column)
        return expr

    def unary(self) -> ASTNode:
        """Unary -> ('!' | '-' | '+') Unary | Primary"""
        if self._match(TokenType.NOT, TokenType.MINUS, TokenType.PLUS):
            op_token = self._previous()
            self._log_rule(f"Unary -> '{op_token.value}' Unary")
            right = self.unary()
            return UnaryOpNode(str(op_token.value), right, op_token.line, op_token.column)
        return self.primary()

    def primary(self) -> ASTNode:
        """
        Primary -> INT_LIT | FLOAT_LIT | STRING_LIT | BOOL_LIT | IDENTIFIER | '(' Expression ')'
        """
        curr = self._peek()

        if self._match(TokenType.INT_LIT):
            self._log_rule(f"Primary -> INT_LIT ({curr.value})")
            return LiteralNode("int", curr.value, curr.line, curr.column)

        if self._match(TokenType.FLOAT_LIT):
            self._log_rule(f"Primary -> FLOAT_LIT ({curr.value})")
            return LiteralNode("float", curr.value, curr.line, curr.column)

        if self._match(TokenType.STRING_LIT):
            self._log_rule(f"Primary -> STRING_LIT (\"{curr.value}\")")
            return LiteralNode("string", curr.value, curr.line, curr.column)

        if self._match(TokenType.BOOL_LIT):
            self._log_rule(f"Primary -> BOOL_LIT ({curr.value})")
            return LiteralNode("bool", curr.value, curr.line, curr.column)

        if self._match(TokenType.IDENTIFIER):
            self._log_rule(f"Primary -> IDENTIFIER ({curr.value})")
            return IdentifierNode(str(curr.value), curr.line, curr.column)

        if self._match(TokenType.LPAREN):
            paren_token = self._previous()
            self._log_rule("Primary -> '(' Expression ')'")
            expr = self.expression()
            self._consume(TokenType.RPAREN, "Expected matching closing ')' in expression")
            return expr

        raise ParseException(f"Expected expression, but found '{curr.value}'", curr)
