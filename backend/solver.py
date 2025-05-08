import re
from sympy import symbols, Eq, sympify, solve, expand, factor, simplify, sqrt, log, exp
from sympy import solve_poly_system, Poly, together, powsimp, Symbol
from sympy.core.relational import Relational, Equality, StrictLessThan, LessThan, StrictGreaterThan, GreaterThan
from sympy.solvers.inequalities import solve_univariate_inequality
from sympy.printing.latex import latex

x = symbols("x")

def preprocess(expression: str) -> str:
    """
    Preprocess the expression to handle implicit multiplication.
    """
    # Insert * between number and variable, e.g., 2x → 2*x
    expression = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expression)
    # Insert * between closing parenthesis and variable/number, e.g., (x+1)y → (x+1)*y
    expression = re.sub(r'(\))([a-zA-Z0-9])', r'\1*\2', expression)
    # Insert * between variable and opening parenthesis, e.g., x(y+1) → x*(y+1)
    expression = re.sub(r'([a-zA-Z0-9])(\()', r'\1*\2', expression)
    return expression

def solve_equation_with_steps(expr_str: str) -> dict:
    """
    Solve an equation and return steps and solution in LaTeX format.
    """
    try:
        # Preprocess the expression
        expr_str = preprocess(expr_str)
        
        # Check if it's an inequality
        if any(symbol in expr_str for symbol in [">=", "<=", ">", "<", "!="]):
            for symbol in [">=", "<=", ">", "<", "!="]:
                if symbol in expr_str:
                    left, right = expr_str.split(symbol, 1)
                    return solve_inequality_with_steps(left, symbol, right)
        
        # Otherwise, treat as equation
        if "=" in expr_str:
            left, right = expr_str.split("=")
            return solve_simple_equation_with_steps(left, right)
        else:
            # Treat as expression to simplify
            expr = sympify(expr_str)
            return {
                "steps": f"Simplifying expression: ${latex(expr)}$\nResult: ${latex(simplify(expr))}$",
                "solution": f"${latex(simplify(expr))}$"
            }
        
    except Exception as e:
        return {
            "steps": f"Error solving equation: {str(e)}",
            "solution": f"Error: {str(e)}"
        }

def solve_simple_equation_with_steps(left: str, right: str) -> dict:
    """
    Solve a simple equation and return steps in LaTeX format.
    """
    steps = []
    left_expr = sympify(left)
    right_expr = sympify(right)
    steps.append(f"Original equation: ${latex(Eq(left_expr, right_expr))}$")
    
    # Move all terms to the left side
    expr = left_expr - right_expr
    steps.append(f"Rearranging to standard form: ${latex(expr)} = 0$")
    
    # Expand the expression
    expanded = expand(expr)
    if expanded != expr:
        steps.append(f"Expanding: ${latex(expanded)} = 0$")
        expr = expanded
    
    # Try to factor if possible
    factored = factor(expr)
    if factored != expr:
        steps.append(f"Factoring: ${latex(factored)} = 0$")
    
    # Solve the equation
    try:
        solution = solve(Eq(expr, 0), x)
        solution_latex = ", ".join(f"x = {latex(sol)}" for sol in solution)
        steps.append(f"Solution: ${solution_latex}$")
    except Exception as e:
        steps.append(f"Error in solving: {str(e)}")
        solution = ["Unable to solve"]
        solution_latex = "Unable to solve"
    
    return {
        "steps": "\n".join(steps),
        "solution": f"${solution_latex}$"
    }

def solve_inequality_with_steps(left: str, symbol: str, right: str) -> dict:
    """
    Solve an inequality and return steps in LaTeX format.
    """
    steps = []
    left_expr = sympify(left)
    right_expr = sympify(right)
    # Map symbol to LaTeX
    latex_symbol = {
        ">": ">",
        ">=": "\\geq",
        "<": "<",
        "<=": "\\leq",
        "!=": "\\neq"
    }[symbol]
    steps.append(f"Original inequality: ${latex(left_expr)} {latex_symbol} {latex(right_expr)}$")
    
    # Move all terms to the left side
    expr = left_expr - right_expr
    steps.append(f"Rearranging to standard form: ${latex(expr)} {latex_symbol} 0$")
    
    # Create the inequality
    if symbol == ">":
        ineq = expr > 0
    elif symbol == ">=":
        ineq = expr >= 0
    elif symbol == "<":
        ineq = expr < 0
    elif symbol == "<=":
        ineq = expr <= 0
    elif symbol == "!=":
        # For != inequality, we'll need different handling
        solution = solve(expr, x)
        solution_latex = ", ".join(f"x \\neq {latex(sol)}" for sol in solution)
        steps.append(f"Solution: ${solution_latex}$")
        return {
            "steps": "\n".join(steps),
            "solution": f"${solution_latex}$"
        }
    
    # Try to solve the inequality
    try:
        solution = solve_univariate_inequality(ineq, x)
        steps.append(f"Solution: ${latex(solution)}$")
    except Exception as e:
        steps.append(f"Error solving inequality: {str(e)}")
        # Manual approach for simple linear inequalities
        try:
            coeff = expr.coeff(x, 1)  # Get coefficient of x
            const = expr.subs(x, 0)   # Get constant term
            
            if coeff != 0:
                if symbol in [">", ">="]:
                    if coeff > 0:
                        solution_latex = f"x {latex_symbol} {latex(-const/coeff)}"
                    else:
                        # Flip the inequality if coefficient is negative
                        flipped_symbol = "<" if symbol == ">" else "\\leq"
                        solution_latex = f"x {flipped_symbol} {latex(-const/coeff)}"
                elif symbol in ["<", "<="]:
                    if coeff > 0:
                        solution_latex = f"x {latex_symbol} {latex(-const/coeff)}"
                    else:
                        # Flip the inequality if coefficient is negative
                        flipped_symbol = ">" if symbol == "<" else "\\geq"
                        solution_latex = f"x {flipped_symbol} {latex(-const/coeff)}"
                    
                steps.append(f"Manual solution: ${solution_latex}$")
                solution = solution_latex.replace("$", "")
            else:
                # Coefficient of x is 0, inequality is always true or always false
                if (symbol == ">" and const > 0) or (symbol == ">=" and const >= 0) or \
                   (symbol == "<" and const < 0) or (symbol == "<=" and const <= 0):
                    solution = "All real numbers"
                else:
                    solution = "No solution"
                steps.append(f"Solution: ${solution}$")
        except Exception as e2:
            steps.append(f"Manual method failed: {str(e2)}")
            solution = "Unable to solve"
            steps.append(f"Solution: ${solution}$")
    
    return {
        "steps": "\n".join(steps),
        "solution": f"${latex(solution)}$" if solution != "All real numbers" and solution != "No solution" else solution
    }

def solve_equation(expr: str) -> str:
    """
    Original function for backward compatibility.
    """
    result = solve_equation_with_steps(expr)
    return result["solution"]

