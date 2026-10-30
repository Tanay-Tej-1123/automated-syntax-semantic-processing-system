"""
Unit and Integration Test Suite for Compiler Design Mini-Project
Automated Syntax and Semantic Analysis System
"""

import sys
import unittest
from lexer import Lexer, TokenType
from parser import Parser
from semantic import SemanticAnalyzer
from samples import SAMPLE_PROGRAMS, get_samples_dict


class TestCompilerPipeline(unittest.TestCase):

    def test_lexer_token_types(self):
        code = 'int a = 10; float b = 3.14; bool c = true; string d = "text";'
        lexer = Lexer(code)
        tokens, errors = lexer.tokenize()

        self.assertEqual(len(errors), 0, "Lexer should have 0 errors for basic variable declarations")
        token_types = [t.type for t in tokens if t.type != TokenType.EOF]
        expected_types = [
            TokenType.KEYWORD_INT, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.INT_LIT, TokenType.SEMICOLON,
            TokenType.KEYWORD_FLOAT, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.FLOAT_LIT, TokenType.SEMICOLON,
            TokenType.KEYWORD_BOOL, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.BOOL_LIT, TokenType.SEMICOLON,
            TokenType.KEYWORD_STRING, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.STRING_LIT, TokenType.SEMICOLON
        ]
        self.assertEqual(token_types, expected_types)

    def test_lexer_error_detection(self):
        code = 'int $badChar = 5; string s = "unclosed string;'
        lexer = Lexer(code)
        tokens, errors = lexer.tokenize()

        self.assertGreater(len(errors), 0, "Lexer should report errors for invalid character and unclosed string")
        messages = " ".join([e.message for e in errors])
        self.assertIn("Unexpected or illegal character", messages)
        self.assertIn("Unterminated string literal", messages)

    def test_valid_factorial(self):
        samples = get_samples_dict()
        code = samples["valid_factorial"]["code"]

        lexer = Lexer(code)
        tokens, lex_errors = lexer.tokenize()
        self.assertEqual(len(lex_errors), 0)

        parser = Parser(tokens)
        ast, syn_errors, _ = parser.parse()
        self.assertEqual(len(syn_errors), 0)
        self.assertIsNotNone(ast)

        analyzer = SemanticAnalyzer()
        symbols, sem_errors, _ = analyzer.analyze(ast)
        self.assertEqual(len(sem_errors), 0)

        sym_names = [s["name"] for s in symbols]
        self.assertIn("n", sym_names)
        self.assertIn("fact", sym_names)
        self.assertIn("counter", sym_names)

    def test_valid_scoping_and_shadowing(self):
        samples = get_samples_dict()
        code = samples["valid_scoping"]["code"]

        lexer = Lexer(code)
        tokens, lex_errors = lexer.tokenize()
        self.assertEqual(len(lex_errors), 0)

        parser = Parser(tokens)
        ast, syn_errors, _ = parser.parse()
        self.assertEqual(len(syn_errors), 0)

        analyzer = SemanticAnalyzer()
        symbols, sem_errors, _ = analyzer.analyze(ast)
        self.assertEqual(len(sem_errors), 0)

        # There should be two symbols named globalVar (one global, one shadowed in block)
        global_vars = [s for s in symbols if s["name"] == "globalVar"]
        self.assertEqual(len(global_vars), 2, "Should capture outer and shadowed variable declarations")

    def test_invalid_syntax_recovery(self):
        samples = get_samples_dict()
        code = samples["invalid_syntax"]["code"]

        lexer = Lexer(code)
        tokens, _ = lexer.tokenize()

        parser = Parser(tokens)
        ast, syn_errors, _ = parser.parse()
        self.assertGreater(len(syn_errors), 0, "Parser must identify syntax errors")

    def test_invalid_semantic_declaration(self):
        samples = get_samples_dict()
        code = samples["invalid_semantic_declaration"]["code"]

        lexer = Lexer(code)
        tokens, _ = lexer.tokenize()

        parser = Parser(tokens)
        ast, _, _ = parser.parse()

        analyzer = SemanticAnalyzer()
        _, sem_errors, _ = analyzer.analyze(ast)

        error_types = [e.error_type for e in sem_errors]
        self.assertIn("DuplicateDeclaration", error_types, "Must catch duplicate declaration in same scope")
        self.assertIn("UndeclaredVariable", error_types, "Must catch use of undeclared variable")

    def test_invalid_semantic_type(self):
        samples = get_samples_dict()
        code = samples["invalid_semantic_type"]["code"]

        lexer = Lexer(code)
        tokens, _ = lexer.tokenize()

        parser = Parser(tokens)
        ast, _, _ = parser.parse()

        analyzer = SemanticAnalyzer()
        _, sem_errors, _ = analyzer.analyze(ast)

        error_types = [e.error_type for e in sem_errors]
        self.assertIn("TypeMismatch", error_types, "Must catch type mismatch in assignment or arithmetic")
        self.assertIn("DivisionByZero", error_types, "Must catch division by constant zero")
        self.assertIn("ConditionTypeError", error_types, "Must catch non-boolean if condition")


def run_all_tests():
    print("=" * 70)
    print("AUTOMATED SYNTAX AND SEMANTIC ANALYSIS SYSTEM - UNIT TESTS")
    print("=" * 70)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCompilerPipeline)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
