"""
Sample Programs (Valid & Invalid Test Cases) for MiniLang
Automated Syntax and Semantic Analysis System
"""

from typing import Dict, Any, List

SAMPLE_PROGRAMS: List[Dict[str, Any]] = [
    {
        "id": "valid_factorial",
        "title": "Valid: Factorial & Loop Calculation",
        "category": "Valid",
        "description": "Calculates factorial of a number using while loop, arithmetic operations, and print statements.",
        "code": """// MiniLang Program: Factorial Calculation
int n = 5;
int fact = 1;
int counter = 1;

while (counter <= n) {
    fact = fact * counter;
    counter = counter + 1;
}

print(fact);
"""
    },
    {
        "id": "valid_temperature",
        "title": "Valid: Temperature Classifier (If-Else & Floats)",
        "category": "Valid",
        "description": "Uses float literals, relational comparisons, and branched if-else blocks.",
        "code": """// MiniLang Program: Temperature Checker
float celsius = 37.5;
float fahrenheit = (celsius * 1.8) + 32.0;

bool isFever = false;
if (fahrenheit > 98.6) {
    isFever = true;
    print("Warning: Elevated Temperature");
} else {
    isFever = false;
    print("Normal Body Temperature");
}

print(fahrenheit);
"""
    },
    {
        "id": "valid_scoping",
        "title": "Valid: Nested Scopes & Variable Shadowing",
        "category": "Valid",
        "description": "Demonstrates block scopes { ... }, symbol resolution up the scope tree, and valid shadowing.",
        "code": """// MiniLang Program: Nested Block Scopes
int globalVar = 100;
string status = "active";

{
    // Inner block 1
    int innerVal = 50;
    int globalVar = 200; // Shadows outer globalVar in this block
    print(globalVar + innerVal);
}

{
    // Inner block 2
    int secondInner = 75;
    print(globalVar + secondInner);
}

print(status);
"""
    },
    {
        "id": "valid_boolean_logic",
        "title": "Valid: Logical Expressions & String Concatenation",
        "category": "Valid",
        "description": "Demonstrates logical operators (&&, ||, !), equality checking, and string concatenation.",
        "code": """// MiniLang Program: Boolean and Strings
bool hasID = true;
bool isRegistered = false;
int age = 21;

bool canEnter = (hasID && isRegistered) || (age >= 18);

string greeting = "Access Granted: " + "Student verified";
if (canEnter) {
    print(greeting);
} else {
    print("Access Denied");
}
"""
    },
    {
        "id": "invalid_lexical",
        "title": "Invalid: Lexical Errors (Illegal Chars & Unclosed String)",
        "category": "Invalid - Lexical",
        "description": "Contains unrecognized characters (@, #) and an unterminated string literal.",
        "code": """// MiniLang Program: Lexical Errors Demonstration
int score = 95;
float rate = 3.5;

// Illegal symbol '@' and '#'
int @invalidToken = 10;
int hexCode = #FF00;

// Unterminated string literal
string message = "This string has no closing quote;

print(score);
"""
    },
    {
        "id": "invalid_syntax",
        "title": "Invalid: Syntax Errors (Missing Semicolons & Braces)",
        "category": "Invalid - Syntax",
        "description": "Contains missing semicolon, unclosed parenthesis in loop condition, and missing closing brace.",
        "code": """// MiniLang Program: Syntax Errors Demonstration
int a = 10
int b = 20;

// Missing closing parenthesis in while condition
while (a < b {
    a = a + 1;
}

// Missing closing brace for if block
if (b > 10) {
    print(b);
// Missing '}' here
"""
    },
    {
        "id": "invalid_semantic_declaration",
        "title": "Invalid: Semantic Errors (Undeclared & Duplicate Variables)",
        "category": "Invalid - Semantic",
        "description": "Attempts to use undeclared variables and redeclares a variable in the same scope.",
        "code": """// MiniLang Program: Declaration Semantic Errors
int count = 10;

// Duplicate declaration in the same scope
float count = 25.5;

// Using undeclared variable 'total'
total = count + 5;

// Referencing undeclared variable 'missingVar' in print
print(missingVar);
"""
    },
    {
        "id": "invalid_semantic_type",
        "title": "Invalid: Semantic Errors (Type Mismatch & Division by Zero)",
        "category": "Invalid - Semantic",
        "description": "Violates type checking (assigning string to int, bool in arithmetic) and division by zero.",
        "code": """// MiniLang Program: Type Mismatch and Zero Division
int x = "hello world"; // Cannot assign string to int

bool flag = true;
int sum = 50 + flag;   // Incompatible arithmetic operand 'bool'

int divisor = 0;
int result = 100 / 0;  // Division by zero constant!

// Condition in 'if' statement must evaluate to bool
if ("not a boolean") {
    print("Won't work");
}
"""
    }
]


def get_samples_dict() -> Dict[str, Any]:
    return {sample["id"]: sample for sample in SAMPLE_PROGRAMS}
