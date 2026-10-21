"""JAX-free view of randomize.py constants for box tests."""
import ast, os
_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'randomize.py'), encoding='utf-8').read()
ROBOT_MASS_RANGE = next(ast.literal_eval(n.value) for n in ast.parse(_src).body
                        if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'ROBOT_MASS_RANGE')
