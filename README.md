# Automated Syntax and Semantic Analysis System

**A Complete B.Tech Compiler Design Mini-Project & Interactive Diagnostic Dashboard**

Developed for the **Compiler Design / Language Processors** curriculum (B.Tech CSE/IT). This tool provides an end-to-end, real implementation of the first three fundamental phases of a compiler: **Lexical Analysis**, **Syntax Analysis**, and **Semantic Analysis**, integrated with a modern Flask REST backend and an interactive web dashboard.

---

## 🌟 Key Features

1. **Real Compiler Implementation (No Hardcoded Mockups):**
   - **Lexer:** Scans raw source code character-by-character, recognizes keywords, identifiers, numeric/string/boolean literals, operators, and delimiters, tracks precise line and column numbers, and catches unclosed strings/comments and illegal characters.
   - **Parser:** An LL(1) **Recursive Descent Parser** implementing operator precedence climbing. Generates an **Abstract Syntax Tree (AST)** and logs the grammar derivation production rules.
   - **Semantic Analyzer:** Implements a **Hierarchical Scoped Symbol Table** (supporting block scopes `{ ... }` and variable shadowing), enforces declaration-before-use, checks for duplicate declarations in the same scope, validates type compatibility in initializations, assignments, and binary/unary expressions, verifies loop/branch conditional guard types, and detects compile-time division by zero.
2. **Interactive Web Dashboard:**
   - Real-time or on-demand analysis (`Ctrl + Enter`).
   - Split-screen workspace: Code editor with line numbers, quick-sample pills, and a 5-tab analysis inspector.
   - **Collapsible AST Tree View** with colored node badges and Expand/Collapse controls.
   - **Filtered Token Stream Table** by category (Keywords, Identifiers, Literals, Operators, Delimiters).
   - **Scoped Symbol Table** displaying identifier, type, scope level/name, line/column, and initialization state.
   - **Export Analysis Report** as a JSON diagnostic artifact.
3. **Pre-configured Test Suite:**
   - 4 Valid programs (Factorial loop, Temperature converter with if-else, Scoped blocks with shadowing, Boolean logic with string concatenation).
   - 4 Invalid programs (Lexical illegal symbols, Syntax missing semicolons/braces, Semantic undeclared/duplicate variables, Semantic type mismatches and division by zero).

---

## 📐 MiniLang Formal Grammar Specification (EBNF)

The system parses **MiniLang**, a statically typed, C-like pedagogical language defined by the following Extended Backus-Naur Form (EBNF) grammar:

```ebnf
Program         ::= Statement* EOF

Statement       ::= VarDecl
                  | Assignment
                  | IfStatement
                  | WhileStatement
                  | PrintStatement
                  | BlockStatement

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
Primary         ::= INT_LIT
                  | FLOAT_LIT
                  | STRING_LIT
                  | BOOL_LIT
                  | IDENTIFIER
                  | '(' Expression ')'
```

### Operator Precedence Hierarchy (Highest to Lowest)
1. **Primary & Parentheses:** `( )`, Literals, Identifiers
2. **Unary:** `!`, unary `-`, unary `+`
3. **Multiplicative:** `*`, `/`, `%`
4. **Additive:** `+` (addition & string concatenation), `-`
5. **Relational:** `<`, `<=`, `>`, `>=`
6. **Equality:** `==`, `!=`
7. **Logical AND:** `&&`
8. **Logical OR:** `||`
9. **Assignment:** `=`

---

## 📂 Project Architecture & File Structure

```
automated_compiler_system/
├── app.py                  # Flask web backend with REST API (/api/analyze, /api/samples, /api/grammar)
├── lexer.py                # Lexical Analyzer (Tokenizer with line/column tracking & error detection)
├── ast_nodes.py            # AST Node hierarchy (Program, VarDecl, Assignment, BinaryOp, If, While, etc.)
├── parser.py               # Recursive Descent Syntax Parser with AST generation & error recovery
├── semantic.py             # Scoped Symbol Table, Type Checker, and Semantic Diagnostics
├── samples.py              # Suite of valid and invalid sample programs with descriptions
├── test_compiler.py        # Automated unit test suite testing Lexer, Parser, and Semantic Analyzer
├── test_api.py             # Automated end-to-end API test suite testing Flask endpoints
├── run_server.py           # Standalone runner script to start the web application
├── requirements.txt        # Python dependencies (Flask >= 3.0.0)
├── README.md               # Complete documentation, presentation guide, and viva Q&A
├── templates/
│   └── index.html          # Clean, modern B.Tech project presentation dashboard
└── static/
    ├── css/
    │   └── style.css       # Responsive dark-theme dashboard with custom badges and tree views
    └── js/
        └── main.js         # Interactive UI logic, keyboard shortcuts, AST viewer, and filters
```

---

## ⚙️ How Each Compiler Phase Works

### Phase 1: Lexical Analysis (`lexer.py`)
- **Input:** Raw character stream of MiniLang source code.
- **Mechanism:**
  - Advances character pointer while maintaining line and column counters.
  - Strips whitespace and single-line (`//`) / multi-line (`/* ... */`) comments.
  - Recognizes keywords (`int`, `float`, `bool`, `string`, `if`, `else`, `while`, `print`, `true`, `false`) via lookup table.
  - Lexes identifiers (`[a-zA-Z_][a-zA-Z0-9_]*`), integer literals (`[0-9]+`), float literals (`[0-9]+\.[0-9]+`), and escaped strings (`"..."`).
  - Distinguishes single-character from two-character operators (e.g. `=` vs `==`, `!` vs `!=`, `<` vs `<=`, `>` vs `>=`).
- **Error Handling:** Identifies illegal characters (e.g., `@`, `#`) and unterminated string/comment tokens with exact line and column numbers.

### Phase 2: Syntax Analysis (`parser.py`)
- **Input:** Stream of tokens from the Lexer.
- **Mechanism:**
  - Uses an LL(1) **Recursive Descent Parser** where each grammar rule corresponds to a parsing method.
  - Precedence climbing implements unambiguous parsing of nested mathematical and logical expressions without left recursion.
  - Constructs a strongly typed **Abstract Syntax Tree (AST)** using node classes from `ast_nodes.py`.
- **Error Recovery:** When an unexpected token or missing delimiter (e.g. missing `;`, `)`, `}`) is encountered, the parser records a `SyntaxErrorRecord` and synchronizes to the next statement boundary to discover subsequent errors.

### Phase 3: Semantic Analysis (`semantic.py`)
- **Input:** AST generated by the Parser.
- **Mechanism:**
  - Traverses the AST in visitor pattern order.
  - **Scoped Symbol Table:** Maintains a tree of symbol tables with parent pointers. Entering a block `{ ... }` pushes a new child scope; exiting pops it.
  - **Declaration Checks:** Verifies identifiers are declared before use. Disallows duplicate declarations within the same block scope while allowing legal inner-block shadowing.
  - **Type Checking:** Evaluates expression types bottom-up. Enforces strict type consistency:
    - Assignments require identical types (or safe widening from `int` to `float`).
    - Arithmetic operators require numeric operands (`+` allows string concatenation).
    - Relational and Equality comparisons validate operand compatibility and evaluate to `bool`.
    - Logical operators (`&&`, `||`, `!`) strictly require `bool` operands.
    - Condition expressions in `if` and `while` must evaluate to `bool`.
    - Detects constant division by zero (`x / 0`).

---

## 🚀 Setup & Execution Guide

### 1. Prerequisites
- Python 3.8 or higher installed on your machine.
- Web browser (Chrome, Firefox, Edge, Safari).

### 2. Installation
Open a terminal / command prompt and navigate to the project directory:
```bash
cd automated_compiler_system
pip install -r requirements.txt
```

### 3. Run Unit and Integration Tests
Verify that all compiler phases and API endpoints pass:
```bash
# Run compiler unit tests (Lexer, Parser, Semantic Analyzer)
python test_compiler.py

# Run Flask REST API integration tests
python test_api.py
```

### 4. Start the Application
Run the Flask server:
```bash
python run_server.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Demonstration Test Cases

### 1. Valid Program 1: Factorial & Loop Calculation
```c
// MiniLang Program: Factorial Calculation
int n = 5;
int fact = 1;
int counter = 1;

while (counter <= n) {
    fact = fact * counter;
    counter = counter + 1;
}

print(fact);
```
*Expected Result:*
- **Lexical:** Passed (36 Tokens)
- **Syntax:** Passed (AST generated with `WhileStatement` and `BinaryOp`)
- **Semantic:** Passed (3 symbols in Global scope: `n`, `fact`, `counter`)
- **Verdict:** `Compiled Successfully`

---

### 2. Valid Program 2: Scoping & Variable Shadowing
```c
// MiniLang Program: Nested Block Scopes
int globalVar = 100;
string status = "active";

{
    int innerVal = 50;
    int globalVar = 200; // Legal shadowing
    print(globalVar + innerVal);
}

print(status);
```
*Expected Result:*
- **Verdict:** `Compiled Successfully`
- **Symbol Table:** Shows 2 separate `globalVar` entries (one in `Global`, one in `Block (Level 1)`).

---

### 3. Invalid Program: Lexical Errors
```c
int score = 95;
int @invalidToken = 10;
int hexCode = #FF00;
string message = "Unclosed string;
```
*Expected Result:*
- **Lexical Errors:**
  - `Unexpected or illegal character '@'` at Line 2, Col 5.
  - `Unexpected or illegal character '#'` at Line 3, Col 15.
  - `Unterminated string literal` at Line 4, Col 18.
- **Verdict:** `Compilation Failed`

---

### 4. Invalid Program: Syntax Errors
```c
int a = 10
int b = 20;

while (a < b {
    a = a + 1;
}
```
*Expected Result:*
- **Syntax Errors:**
  - `Missing semicolon ';' after declaration of 'a'` at Line 1.
  - `Expected ')' after while-condition` at Line 4.

---

### 5. Invalid Program: Semantic Errors
```c
int count = 10;
float count = 25.5; // Duplicate declaration
total = count + 5;  // Undeclared variable 'total'
int x = "hello";    // Type mismatch
int result = 10 / 0;// Division by zero
if (123) {          // Non-boolean condition
    print("test");
}
```
*Expected Result:*
- **Semantic Errors:**
  - `DuplicateDeclaration: Variable 'count' is already declared in scope 'Global'`
  - `UndeclaredVariable: Variable 'total' is assigned before declaration`
  - `TypeMismatch: Cannot initialize variable 'x' of type 'int' with incompatible type 'string'`
  - `DivisionByZero: Division or modulo by zero constant detected`
  - `ConditionTypeError: Condition in 'if' statement must evaluate to 'bool', but found type 'int'`

---

## 🎓 Viva Voce Preparation Guide (B.Tech Questions & Answers)

### Q1. What is the difference between Syntax and Semantic Analysis?
> **Answer:** **Syntax analysis** checks whether the input string adheres to the grammatical rules of the programming language (context-free grammar). It does not know if variables exist or if operations make sense. **Semantic analysis** examines the *meaning* and *context* of the program—verifying that variables are declared before use, types in expressions and assignments are compatible, and scoping rules are respected.

### Q2. Why did you choose a Recursive Descent Parser?
> **Answer:** Recursive descent is a top-down LL(1) parsing technique that maps directly to high-level language constructs. Each non-terminal in our MiniLang grammar is represented by a dedicated Python function (e.g., `statement()`, `var_declaration()`, `expression()`). It allows explicit control over error reporting and synchronization, and with precedence climbing, it elegantly parses expressions with standard arithmetic precedence.

### Q3. How does your compiler resolve variable scope and shadowing?
> **Answer:** The semantic analyzer uses a **hierarchical tree of Symbol Tables**. When the parser enters a block `{ ... }`, a child `SymbolTable` is instantiated with its `parent` pointer referencing the enclosing scope. When looking up an identifier:
> 1. It first queries `symbols` in the current scope.
> 2. If not found, it recursively queries the `parent` scope until it reaches `Global`.
> 3. If still not found, it raises an `UndeclaredVariable` error.
> Redeclarations are checked strictly against the current scope, allowing legal shadowing of outer variables in inner blocks.

### Q4. Can an `int` be assigned to a `float` in your language?
> **Answer:** Yes. Our type-checker implements **implicit widening coercion**: an `int` can be safely promoted to a `float` because it is a non-lossy widening conversion. However, assigning a `float` or a `string` to an `int` triggers a `TypeMismatch` error.

### Q5. What is the role of the Abstract Syntax Tree (AST)?
> **Answer:** An AST is a condensed, hierarchical tree representation of the source code that strips away syntactic boilerplate (like parentheses, commas, and semicolons) while retaining operator-operand relationships and program structure. It serves as the primary data structure passed to the semantic analyzer and future code generation phases.

---

## 🏆 Project Presentation Tips

1. **Start with the Problem & Objective:** Present the tool as an automated teaching and diagnostic compiler frontend designed to help students and developers visualize compiler internals.
2. **Show the Valid Factorial Program First:** Run the Factorial sample to demonstrate successful end-to-end execution across all three phases with green badges, populated tokens, interactive AST, and symbol table.
3. **Demonstrate Error Handling Live:** Load the invalid samples one by one to show how each compiler phase isolates and reports specific classes of errors with line and column numbers.
4. **Walk Through the AST:** Click on AST nodes to show parent-child relationships and explain how the recursive descent parser built the tree following the EBNF grammar.
5. **Show the Symbol Table:** Highlight how scoped blocks maintain separate variable bindings and prevent duplicate declarations.
