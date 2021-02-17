import sys, ast
import base64

exp = base64.b64decode('<<< CODE >>>').decode('utf-8')

node = ast.parse(exp, mode='exec')
flag = 'ctf{000000000000000000000000000000}'

class SafetyInspector(ast.NodeVisitor):
	def visit(self, node):
		if isinstance(node, ast.Call):
			raise Exception('security_error')

		super().generic_visit(node)

SafetyInspector().visit(node)

exec(exp)
