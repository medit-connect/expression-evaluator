# class definition for basic operations
class Operator:
	def __init__(self, opeartor, function, description=''):
		self.operator = opeartor
		self.function = function
		self.description = description

	def is_binary(self):
		return self.function.__code__.co_argcount == 2

	def is_unary(self):
		return self.function.__code__.co_argcount == 1

	@staticmethod
	def float_converter(value):
		try:
			return float(value)
		except (ValueError, TypeError):
			return value

	@staticmethod
	def int_converter(value):
		try:
			return int(float(value))
		except (ValueError, TypeError):
			return value

	@staticmethod
	def bool_converter(value):
		try:
			if type(value) is str:
				if value.lower() == 'true':
					return True
				elif value.lower() == 'false':
					return False
				else:
					return bool(float(value))
			else:
				return bool(value)
		except (ValueError, TypeError):
			return value

__logical_op_set = (
	Operator('|', lambda x, y: x or y, 'logical or'),
	Operator('&', lambda x, y: x and y, 'logical and'),
	(
		Operator('=', lambda x, y: x == y, 'logical equality'),
		Operator('≠', lambda x, y: x != y, 'logical inequality')
	),
	Operator('!', lambda x: not x, 'logical not')
)

__arithmetic_op_set = (
	(
		Operator('+', lambda x, y: x + y, 'addition'),
		Operator('-', lambda x, y: x - y, 'subtraction')
	),
	(
		Operator('*', lambda x, y: x * y, 'multiplication'),
		Operator('/', lambda x, y: x / y, 'division')
	)
)

def logicalOperatorSet():
	return __logical_op_set

def arithmeticOperatorSet():
	return __arithmetic_op_set

def _convert_infix_to_postfix(exp, operators=arithmeticOperatorSet(), br_open='(', br_close=')'):
	def find_op(tok, ops):
		for i in range(len(ops)):
			for op in ops[i] if isinstance(ops[i], (list, tuple)) else [ops[i]]:
				if len(op) <= len(tok):
					if tok[-len(op):] == op:
						return i, op, tok[:len(tok)-len(op)].strip()
		return -1, None, None

	ops = [br_open, br_close]
	op2op = {}
	for op in operators:
		if isinstance(op, Operator):
			ops.append(op.operator)
			op2op[op.operator] = op
		else:
			ops.append([x.operator for x in op])
			for x in op: op2op[x.operator] = x

	infixes, postfixes = [], []
	f, l = 0, 1
	while l <= len(exp):
		if exp[f:l].strip():
			order, op, lhs = find_op(exp[f:l].strip(), ops)
			if order > -1:
				f = l
				if lhs:
					postfixes.append((lhs, None))
				if (op == br_open) or (op in op2op and op2op[op].is_unary()):
					infixes.append((op, order))
				elif op == br_close:
					while infixes[-1][0] != br_open:
						infix = infixes.pop()
						postfixes.append((infix[0], op2op[infix[0]]))
					infixes.pop()
				else:
					while infixes and order <= infixes[-1][1]:
						infix = infixes.pop()
						postfixes.append((infix[0], op2op[infix[0]]))
					infixes.append((op, order))
		l += 1

	if exp[f:].strip():
		postfixes.append((exp[f:].strip(), None))
	while infixes:
		infix = infixes.pop()
		postfixes.append((infix[0], op2op[infix[0]]))
	return postfixes

def _evaluate_postfix_notation(postfixes, converter=Operator.float_converter):
	op_swaparg = lambda x, y: op.function(y, x)
	vstack = []
	# unary_op = None
	for tok, op in postfixes:
		if not op:
			vstack.append(converter(tok))
			# if unary_op:
		elif op.is_unary():
			# if vstack:
			vstack.append(op.function(vstack.pop()))
			# else:
			# 	unary_op = op
		else:
			vstack.append(op_swaparg(vstack.pop(), vstack.pop()))
	return vstack.pop()

def evaluate(expression, operators=arithmeticOperatorSet(), br_open='(', br_close=')', converter=Operator.float_converter):
	postfixes = _convert_infix_to_postfix(expression, operators, br_open, br_close)
	return _evaluate_postfix_notation(postfixes, converter)
