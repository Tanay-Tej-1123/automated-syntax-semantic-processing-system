"""
Lexical Analyzer (Lexer / Tokenizer) for MiniLang
Automated Syntax and Semantic Analysis System
"""

from enum import Enum, auto
from typing import List, Optional, Tuple, Dict, Any


class TokenType(Enum):
    # Keywords
    KEYWORD_INT = "KEYWORD_INT"
    KEYWORD_FLOAT = "KEYWORD_FLOAT"
    KEYWORD_BOOL = "KEYWORD_BOOL"
    KEYWORD_STRING = "KEYWORD_STRING"
    KEYWORD_IF = "KEYWORD_IF"
    KEYWORD_ELSE = "KEYWORD_ELSE"
    KEYWORD_WHILE = "KEYWORD_WHILE"
    KEYWORD_PRINT = "KEYWORD_PRINT"

    # Literals
    INT_LIT = "INT_LIT"
    FLOAT_LIT = "FLOAT_LIT"
    STRING_LIT = "STRING_LIT"
    BOOL_LIT = "BOOL_LIT"

    # Identifier
    IDENTIFIER = "IDENTIFIER"

    # Arithmetic Operators
    PLUS = "PLUS"               # +
    MINUS = "MINUS"             # -
    STAR = "STAR"               # *
    SLASH = "SLASH"             # /
    PERCENT = "PERCENT"         # %

    # Relational Operators
    EQ = "EQ"                   # ==
    NEQ = "NEQ"                 # !=
    LT = "LT"                   # <
    LTE = "LTE"                 # <=
    GT = "GT"                   # >
    GTE = "GTE"                 # >=

    # Logical Operators
    AND = "AND"                 # &&
    OR = "OR"                   # ||
    NOT = "NOT"                 # !

    # Assignment
    ASSIGN = "ASSIGN"           # =

    # Delimiters
    LPAREN = "LPAREN"           # (
    RPAREN = "RPAREN"           # )
    LBRACE = "LBRACE"           # {
    RBRACE = "RBRACE"           # }
    SEMICOLON = "SEMICOLON"     # ;
    COMMA = "COMMA"             # ,

    # End of File
    EOF = "EOF"


KEYWORDS: Dict[str, TokenType] = {
    "int": TokenType.KEYWORD_INT,
    "float": TokenType.KEYWORD_FLOAT,
    "bool": TokenType.KEYWORD_BOOL,
    "string": TokenType.KEYWORD_STRING,
    "if": TokenType.KEYWORD_IF,
    "else": TokenType.KEYWORD_ELSE,
    "while": TokenType.KEYWORD_WHILE,
    "print": TokenType.KEYWORD_PRINT,
    "true": TokenType.BOOL_LIT,
    "false": TokenType.BOOL_LIT,
}


def get_token_category(token_type: TokenType) -> str:
    """Categorize token type for display purposes."""
    name = token_type.name
    if name.startswith("KEYWORD_"):
        return "Keyword"
    elif name in ("INT_LIT", "FLOAT_LIT", "STRING_LIT", "BOOL_LIT"):
        return "Literal"
    elif name == "IDENTIFIER":
        return "Identifier"
    elif name in ("PLUS", "MINUS", "STAR", "SLASH", "PERCENT",
                  "EQ", "NEQ", "LT", "LTE", "GT", "GTE", "AND", "OR", "NOT", "ASSIGN"):
        return "Operator"
    elif name in ("LPAREN", "RPAREN", "LBRACE", "RBRACE", "SEMICOLON", "COMMA"):
        return "Delimiter"
    elif name == "EOF":
        return "Special"
    return "Other"


class Token:
    def __init__(self, token_type: TokenType, value: Any, line: int, column: int):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.name,
            "category": get_token_category(self.type),
            "value": str(self.value),
            "line": self.line,
            "column": self.column
        }

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {repr(self.value)}, Line {self.line}:{self.column})"


class LexicalError:
    def __init__(self, message: str, line: int, column: int, offending_text: str = ""):
        self.message = message
        self.line = line
        self.column = column
        self.offending_text = offending_text

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": "Lexical",
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "offending_text": self.offending_text
        }

    def __repr__(self) -> str:
        return f"LexicalError({self.message} at Line {self.line}:{self.column})"


class Lexer:
    """
    Lexical Analyzer for MiniLang.
    Converts raw source code into a stream of tokens, tracking line and column positions.
    """

    def __init__(self, source_code: str):
        self.source = source_code
        self.length = len(source_code)
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.errors: List[LexicalError] = []

    def _peek(self, offset: int = 0) -> Optional[str]:
        idx = self.position + offset
        if idx < self.length:
            return self.source[idx]
        return None

    def _advance(self) -> Optional[str]:
        if self.position >= self.length:
            return None
        ch = self.source[self.position]
        self.position += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def tokenize(self) -> Tuple[List[Token], List[LexicalError]]:
        """Scan all tokens from the source string."""
        self.tokens = []
        self.errors = []
        self.position = 0
        self.line = 1
        self.column = 1

        while self.position < self.length:
            ch = self._peek()

            # 1. Skip Whitespace
            if ch in (" ", "\t", "\r", "\n"):
                self._advance()
                continue

            # 2. Skip Comments (Single-line '//' and Multi-line '/* ... */')
            if ch == "/" and self._peek(1) == "/":
                # Single-line comment: skip until newline or EOF
                self._advance()  # skip '/'
                self._advance()  # skip '/'
                while self._peek() is not None and self._peek() != "\n":
                    self._advance()
                continue

            if ch == "/" and self._peek(1) == "*":
                # Multi-line comment
                start_line = self.line
                start_col = self.column
                self._advance()  # skip '/'
                self._advance()  # skip '*'
                closed = False
                while self._peek() is not None:
                    if self._peek() == "*" and self._peek(1) == "/":
                        self._advance()  # skip '*'
                        self._advance()  # skip '/'
                        closed = True
                        break
                    self._advance()
                if not closed:
                    self.errors.append(
                        LexicalError(
                            "Unterminated multi-line comment",
                            start_line,
                            start_col,
                            "/*"
                        )
                    )
                continue

            # Remember token start position
            token_line = self.line
            token_col = self.column

            # 3. Numbers (Integer or Float literals)
            if ch.isdigit():
                num_str = ""
                is_float = False
                while self._peek() is not None and (self._peek().isdigit() or self._peek() == "."):
                    if self._peek() == ".":
                        if is_float:
                            # Second decimal point encountered
                            break
                        if self._peek(1) is not None and self._peek(1).isdigit():
                            is_float = True
                        else:
                            # Trailing dot or dot not followed by digit
                            break
                    num_str += self._advance()

                if is_float:
                    self.tokens.append(Token(TokenType.FLOAT_LIT, float(num_str), token_line, token_col))
                else:
                    self.tokens.append(Token(TokenType.INT_LIT, int(num_str), token_line, token_col))
                continue

            # 4. Identifiers and Keywords
            if ch.isalpha() or ch == "_":
                ident_str = ""
                while self._peek() is not None and (self._peek().isalnum() or self._peek() == "_"):
                    ident_str += self._advance()

                if ident_str in KEYWORDS:
                    t_type = KEYWORDS[ident_str]
                    if t_type == TokenType.BOOL_LIT:
                        val = True if ident_str == "true" else False
                        self.tokens.append(Token(TokenType.BOOL_LIT, val, token_line, token_col))
                    else:
                        self.tokens.append(Token(t_type, ident_str, token_line, token_col))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, ident_str, token_line, token_col))
                continue

            # 5. String Literals
            if ch == '"':
                self._advance()  # skip opening quote
                str_val = ""
                is_closed = False
                while self._peek() is not None:
                    curr = self._peek()
                    if curr == "\n":
                        # Unclosed string on the same line
                        break
                    if curr == '"':
                        self._advance()  # skip closing quote
                        is_closed = True
                        break
                    if curr == "\\":
                        # Escape sequences
                        self._advance()
                        esc = self._peek()
                        if esc == "n":
                            str_val += "\n"
                            self._advance()
                        elif esc == "t":
                            str_val += "\t"
                            self._advance()
                        elif esc == '"':
                            str_val += '"'
                            self._advance()
                        elif esc == "\\":
                            str_val += "\\"
                            self._advance()
                        else:
                            str_val += "\\" + (esc if esc else "")
                            if esc:
                                self._advance()
                    else:
                        str_val += self._advance()

                if is_closed:
                    self.tokens.append(Token(TokenType.STRING_LIT, str_val, token_line, token_col))
                else:
                    self.errors.append(
                        LexicalError(
                            "Unterminated string literal",
                            token_line,
                            token_col,
                            f'"{str_val}'
                        )
                    )
                continue

            # 6. Two-character and Single-character Operators / Delimiters
            if ch == "=":
                self._advance()
                if self._peek() == "=":
                    self._advance()
                    self.tokens.append(Token(TokenType.EQ, "==", token_line, token_col))
                else:
                    self.tokens.append(Token(TokenType.ASSIGN, "=", token_line, token_col))
                continue

            if ch == "!":
                self._advance()
                if self._peek() == "=":
                    self._advance()
                    self.tokens.append(Token(TokenType.NEQ, "!=", token_line, token_col))
                else:
                    self.tokens.append(Token(TokenType.NOT, "!", token_line, token_col))
                continue

            if ch == "<":
                self._advance()
                if self._peek() == "=":
                    self._advance()
                    self.tokens.append(Token(TokenType.LTE, "<=", token_line, token_col))
                else:
                    self.tokens.append(Token(TokenType.LT, "<", token_line, token_col))
                continue

            if ch == ">":
                self._advance()
                if self._peek() == "=":
                    self._advance()
                    self.tokens.append(Token(TokenType.GTE, ">=", token_line, token_col))
                else:
                    self.tokens.append(Token(TokenType.GT, ">", token_line, token_col))
                continue

            if ch == "&":
                self._advance()
                if self._peek() == "&":
                    self._advance()
                    self.tokens.append(Token(TokenType.AND, "&&", token_line, token_col))
                else:
                    self.errors.append(
                        LexicalError(
                            "Unrecognized character '&'. Did you mean '&&'?",
                            token_line,
                            token_col,
                            "&"
                        )
                    )
                continue

            if ch == "|":
                self._advance()
                if self._peek() == "|":
                    self._advance()
                    self.tokens.append(Token(TokenType.OR, "||", token_line, token_col))
                else:
                    self.errors.append(
                        LexicalError(
                            "Unrecognized character '|'. Did you mean '||'?",
                            token_line,
                            token_col,
                            "|"
                        )
                    )
                continue

            if ch == "+":
                self._advance()
                self.tokens.append(Token(TokenType.PLUS, "+", token_line, token_col))
                continue

            if ch == "-":
                self._advance()
                self.tokens.append(Token(TokenType.MINUS, "-", token_line, token_col))
                continue

            if ch == "*":
                self._advance()
                self.tokens.append(Token(TokenType.STAR, "*", token_line, token_col))
                continue

            if ch == "/":
                self._advance()
                self.tokens.append(Token(TokenType.SLASH, "/", token_line, token_col))
                continue

            if ch == "%":
                self._advance()
                self.tokens.append(Token(TokenType.PERCENT, "%", token_line, token_col))
                continue

            if ch == "(":
                self._advance()
                self.tokens.append(Token(TokenType.LPAREN, "(", token_line, token_col))
                continue

            if ch == ")":
                self._advance()
                self.tokens.append(Token(TokenType.RPAREN, ")", token_line, token_col))
                continue

            if ch == "{":
                self._advance()
                self.tokens.append(Token(TokenType.LBRACE, "{", token_line, token_col))
                continue

            if ch == "}":
                self._advance()
                self.tokens.append(Token(TokenType.RBRACE, "}", token_line, token_col))
                continue

            if ch == ";":
                self._advance()
                self.tokens.append(Token(TokenType.SEMICOLON, ";", token_line, token_col))
                continue

            if ch == ",":
                self._advance()
                self.tokens.append(Token(TokenType.COMMA, ",", token_line, token_col))
                continue

            # 7. Unrecognized character
            unrecog = self._advance()
            self.errors.append(
                LexicalError(
                    f"Unexpected or illegal character '{unrecog}'",
                    token_line,
                    token_col,
                    str(unrecog)
                )
            )

        # Append EOF Token
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens, self.errors
