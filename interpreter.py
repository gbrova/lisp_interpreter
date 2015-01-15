import re

class Interpreter:
    def __init__(self):
        func_table = {}
        func_table['+'] = lambda l: int(l[0]) + int(l[1])
        func_table['-'] = lambda l: int(l[0]) - int(l[1])
        func_table['*'] = lambda l: int(l[0]) * int(l[1])
        func_table['/'] = lambda l: int(l[0]) / int(l[1])
        func_table['eq?'] = lambda l: l[0] == l[1]

        self.func_table = func_table
        
    def parse(self, expr):
        obj_stack = [[]]
        #TODO: is it faster to use replace instead of re.split()? 
        #expr_tokens = expr.replace('(', ' ( ').replace(')', ' ) ').split(' ')
        
        # Split on the characters space, (, and ).
        # Include the match as part of the resulting list
        expr_tokens = re.split('([ ()])', expr)
        for token in expr_tokens:
            if len(token) == 0 or token == ' ' or token == '\n':
                continue
            if token == '(':
                # TODO: also keep track of a parens stack (e.g. to identify mismatches)
                obj_stack.append([])
            elif token == ')':
                last = obj_stack.pop()
                obj_stack[-1].append(last)
            else:
                obj_stack[-1].append(token)
        return obj_stack[0]

    def is_atom(self, parse_tree):
        return not isinstance(parse_tree, (list, tuple))

    def evaluate(self, parse_tree):
        if self.is_atom(parse_tree):
            value = parse_tree
            try:
                int(value)
                return int(value)
            except ValueError:
                return self.func_table[value]
        fn = parse_tree[0]
        if fn == 'quote':
            # TODO this isn't quite right, because the syntax might have changed somewhat
            return ' '.join([str(item) for item in parse_tree[1:]])
        if fn == 'cons':
            return [parse_tree[1]] + parse_tree[2]
        if fn == 'car':
            return self.evaluate(parse_tree[1][0])
        if fn == 'cdr':
            #TODO should we evaluate here?
            eval_sublist = self.evaluate(parse_tree[1])
            return eval_sublist[1:]
        if fn == 'cond':
            #evaluate each condition until one is True (using Python's comparison)
            for (cond, val_if_true) in parse_tree[1:]:
                if cond == 'else':
                    return self.evaluate(val_if_true)
                if self.evaluate(cond):
                    return self.evaluate(val_if_true)
        if fn == 'define':
            value = self.evaluate(parse_tree[2])
            self.func_table[parse_tree[1]] = value 
            return None
        if fn == 'lambda':
            def cur_fn(values):
                value_names = parse_tree[1]
                lambda_fn = parse_tree[2]
                for (value_name, value) in zip(value_names, values):
                    self.func_table[value_name] = self.evaluate(value)
                result = self.evaluate(lambda_fn)
                for value_name in value_names:
                    del self.func_table[value_name]
                return result
            return cur_fn

        #handle anonymous functions specially, since they won't appear in self.func_table
        if fn[0] == 'lambda':
            args = [self.evaluate(x) for x in parse_tree[1:]]
            return self.evaluate(parse_tree[0]) (args)
        if fn not in self.func_table:
#            print fn
            #TODO: this is hacky, just to get lists to work without '. Remove later. 
            return parse_tree
        else:
            # apply function to everything else in the list
            args = [self.evaluate(x) for x in parse_tree[1:]]
            cur_symbol = self.func_table[parse_tree[0]]
            if callable(cur_symbol):
                return cur_symbol(args)
            else:
                return cur_symbol



import unittest
class TestParse(unittest.TestCase):
    def test_parse(self):
        interpreter = Interpreter()
        result = interpreter.parse('(+ 1 (- 1 2))')
        self.assertEquals([['+', '1', ['-', '1', '2']]], result)

    def test_isAtom(self):
        interpreter = Interpreter()
        tree = interpreter.parse('(+ 1 1)')
        self.assertFalse(interpreter.is_atom(tree))
        self.assertFalse(interpreter.is_atom(tree[0]))
        self.assertTrue(interpreter.is_atom(tree[0][1]))

    def test_evaluate(self):
        interpreter = Interpreter()

        tree1 = interpreter.parse('(+ 1 1)')
        self.assertEquals(2, interpreter.evaluate(tree1[0]))

        tree2 = interpreter.parse('(+ 1 (* 3 2))')
        self.assertEquals(7, interpreter.evaluate(tree2[0]))

    def test_eq(self):
        interpreter = Interpreter()
        tree1 = interpreter.parse('(eq? 1 1)')
        self.assertTrue(interpreter.evaluate(tree1[0]))

        tree2 = interpreter.parse('(eq? 1 2)')
        self.assertFalse(interpreter.evaluate(tree2[0]))

    def test_cons(self):
        interpreter = Interpreter()
        tree = interpreter.parse('(cons 1 (2 3))')
        result = interpreter.evaluate(tree[0])
        self.assertEquals(['1', '2', '3'], result)

    def test_car(self):
        interpreter = Interpreter()
        tree = interpreter.parse('(car (1 2 3))')
        result = interpreter.evaluate(tree[0])
        self.assertEquals(1, result)

    def test_cdr(self):
        interpreter = Interpreter()
        tree = interpreter.parse('(cdr (1 2 3))')
        result = interpreter.evaluate(tree[0])
        self.assertEquals(['2', '3'], result)

        tree = interpreter.parse('(cdr (cdr (1 2 3)))')
        result = interpreter.evaluate(tree[0])
        self.assertEquals(['3'], result)

        tree = interpreter.parse('(cdr (cdr (cdr (1 2 3))))')
        result = interpreter.evaluate(tree[0])
        self.assertEquals([], result)

    def test_define(self):
        interpreter = Interpreter()
        tree = interpreter.parse('(define a 5)')
        interpreter.evaluate(tree[0])
        self.assertEquals(interpreter.evaluate(interpreter.parse('a')[0]), 5)
        self.assertEquals(interpreter.evaluate(interpreter.parse('(+ a 2)')[0]), 7)

        interpreter.evaluate(interpreter.parse('(define b (+ a 1))')[0])
        self.assertEquals(interpreter.evaluate(interpreter.parse('b')[0]), 6)

        self.assertEquals(interpreter.evaluate(interpreter.parse('(+ a b)')[0]), 11)



    def test_lambda(self):
        interpreter = Interpreter()
        tree = interpreter.parse('((lambda (x) (* x x)) 4)')
        self.assertEquals(16, interpreter.evaluate(tree[0]))

        # test it in the context of define
        tree = interpreter.parse('(define square (lambda (x) (* x x)))')
        interpreter.evaluate(tree[0])
        self.assertEquals(25, interpreter.evaluate(interpreter.parse('(square 5)')[0]))

        # test function with multiple args
        tree = interpreter.parse('(define add (lambda (x y) (+ x y)))')
        interpreter.evaluate(tree[0])
        self.assertEquals(11, interpreter.evaluate(interpreter.parse('(add 5 6)')[0]))

        # more complex example
        code = "(define divides_evenly? (lambda (x y) (eq? (* x (/ y x)) (+ y 0))))"
        tree = interpreter.parse(code)
        interpreter.evaluate(tree[0])
        self.assertFalse(interpreter.evaluate(interpreter.parse('(divides_evenly? 6 13)')[0]))
        self.assertTrue(interpreter.evaluate(interpreter.parse('(divides_evenly? 6 12)')[0]))


    def test_quote(self):
        interpreter = Interpreter()
        tree = interpreter.parse('(quote a)')
        self.assertEquals('a', interpreter.evaluate(tree[0]))

        # TODO this might not be the desired behavior
        tree = interpreter.parse('(quote (1 2 3))')
        self.assertEquals("['1', '2', '3']", interpreter.evaluate(tree[0]))

    def test_cond(self):
        interpreter = Interpreter()
        tree = interpreter.parse('(cond ((eq? 1 2) 1) ((eq? 2 2) 2) (else 3))')
        self.assertEquals(2, interpreter.evaluate(tree[0]))

        tree = interpreter.parse('(cond ((eq? 1 2) 1) ((eq? 1 2) 2) (else 3))')
        self.assertEquals(3, interpreter.evaluate(tree[0]))

if __name__ == '__main__':
    unittest.main()


    interpreter = Interpreter()
    tree = interpreter.parse('(+ 1 1)')
    print interpreter.evaluate(tree[0])
    
