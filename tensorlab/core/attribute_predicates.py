"""
Classes for building filtering predicates on attributes.
"""


class Expression:

    is_atomic = False

    def get_leafs(self):
        if self.is_atomic:
            return None
        raise NotImplementedError

    @classmethod
    def parse(cls, string):
        raise NotImplementedError

    def serialize(self):
        raise NotImplementedError


class Identifier(Expression):
    is_atomic = True

    def __init__(self, name):
        self.name = name

    @classmethod
    def parse(cls, string):
        if string[0].isalpha():
            value = string
            for i, c in enumerate(string[1:], 1):
                if not c.isalnum():
                    value = string[:i]
                    break
            if value not in Op.ALL:
                return cls(value), string[len(value):]
        return None, string

    def serialize(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, Identifier) and self.name == other.name

    def __repr__(self):
        return '<Identifier "{}">'.format(self.name)


class Literal(Expression):
    is_atomic = True

    def __init__(self, value):
        self.value = value

    @classmethod
    def parse(cls, string):
        if string[0] in "\"\'":
            escaped = False
            for i, c in enumerate(string[1:], 1):
                if escaped:
                    escaped = False
                elif c == '\\':
                    escaped = True
                elif c in "\"\'":
                    return cls(eval(string[:i+1])), string[i+1:]
        elif string[0].isdigit() or string[0] == '-':
            value = string
            has_dot = False
            for i, c in enumerate(string[1:], 1):
                if c == '.' and not has_dot:
                    has_dot = True
                    continue
                if not c.isdigit():
                    value = string[:i]
                    break
            least_string = string[len(value):]
            value = float(value) if has_dot else int(value)
            return cls(value), least_string
        return None, string

    def serialize(self):
        return repr(self.value)

    def __eq__(self, other):
        return isinstance(other, Literal) and self.value == other.value

    def __repr__(self):
        return '<Literal {!r}>'.format(self.value)


class Op:
    And = 'and'
    Or = 'or'
    Not = 'not'
    Eq = '=='
    Ne = '!='
    Gt = '>'
    Lt = '<'
    Ge = '>='
    Le = '<='

    ALL = (And, Or, Not, Ne, Eq, Gt, Lt, Ge, Le)
    UNARIES = (Not,)
    BINARIES = (And, Or, Ne, Eq, Gt, Lt, Ge, Le)

    priority = {
        Or: 0,
        And: 1,
        Ne: 2,
        Eq: 2,
        Gt: 2,
        Lt: 2,
        Ge: 2,
        Le: 2,
        Not: 3
    }


class UnaryOperation(Expression):

    def __init__(self, op, arg):
        self.op = op
        self.arg = arg

    @classmethod
    def parse(cls, string):
        op, string = _match_op(string, Op.UNARIES)
        if op is not None:
            arg, least_string = _parse_subexpr(string.lstrip())
            if arg is not None:
                return cls(op, arg), least_string
        if op is None:
            if string[0] == '(':
                arg, least_string = _parse_subexpr(string[1:].lstrip())
                least_string = least_string.lstrip()
                if arg is not None and least_string[0] == ')':
                    return arg, least_string[1:]
        return None, string

    def serialize(self):
        if isinstance(self.arg, BinaryOperation):
            if Op.priority[self.op] > Op.priority[self.arg.op]:
                return '{} ({})'.format(self.op, self.arg.serialize())
        return '{} {}'.format(self.op, self.arg.serialize())

    def __eq__(self, other):
        return isinstance(other, UnaryOperation) \
               and self.op == other.op \
               and self.arg == other.arg

    def __repr__(self):
        return '<UnaryOperation "{}" on {!r}>'.format(self.op, self.arg)


class BinaryOperation(Expression):

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    @classmethod
    def parse(cls, string):
        exprs = []
        ops = []
        s = string
        while s and s[0] != ')':
            if s[0] == '(':
                next_expr, next_s = _parse_subexpr(s[1:])
                next_s = next_s.lstrip()
                if not next_s or not next_s.startswith(')'):
                    return None, string
                else:
                    next_s = next_s[1:]
            else:
                next_expr, next_s = _parse_subexpr(s, (UnaryOperation, Identifier, Literal, ))
            if next_expr is None:
                return None, string
            exprs.append(next_expr)
            s = next_s = next_s.lstrip()
            if next_s:
                op, next_s = _match_op(next_s, Op.BINARIES)
                if op is None:
                    break
                s = next_s.lstrip()
                ops.append(op)
            else:
                break
        if len(exprs) < 2:
            return None, string

        def build_tree(exprs_, ops_):
            if len(exprs_) == 1:
                assert len(ops_) == 0
                return exprs_[0]
            idx = min(range(len(ops_)), key=lambda i: Op.priority[ops_[i]])
            op = ops_[idx]
            left = build_tree(exprs_[:idx+1], ops_[:idx])
            right = build_tree(exprs_[idx+1:], ops_[idx+1:])
            return cls(op, left, right)
        return build_tree(exprs, ops), s

    def serialize(self):
        left = self.left.serialize()
        right = self.right.serialize()
        if isinstance(self.left, (BinaryOperation, UnaryOperation)):
            if Op.priority[self.op] > Op.priority[self.left.op]:
                left = '('+left+')'
        if isinstance(self.right, (BinaryOperation, UnaryOperation)):
            if Op.priority[self.op] > Op.priority[self.right.op]:
                right = '('+right+')'
        return '{} {} {}'.format(left, self.op, right)

    def __eq__(self, other):
        return isinstance(other, BinaryOperation) \
               and self.left == other.left \
               and self.op == other.op \
               and self.right == other.right

    def __repr__(self):
        return '<BinaryOperation "{}" on {!r}, {!r}>'.format(
            self.op, self.left, self.right)


def _match_op(string, ops):
    for op in ops:
        if (len(string) > len(op)
                and string.startswith(op)
                and not string[len(op)].isalnum()
                and string[len(op)] != '='):
            return op, string[len(op):]
    return None, string


_ALL_EXPR_TYPES = (BinaryOperation, UnaryOperation, Identifier, Literal, )


def _parse_subexpr(string, expr_types=None):
    if expr_types is None:
        expr_types = _ALL_EXPR_TYPES
    for expr_t in expr_types:
        try:
            expr, least_string = expr_t.parse(string)
        except:
            continue
        else:
            if expr is not None:
                return expr, least_string
    return None, string


def parse_expression(string):
    try:
        e, s = _parse_subexpr(string.strip())
        if len(s.strip()) > 0:
            return None
        return e
    except:
        return None

