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
            if len(token) == 0 or token == ' ':
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

    #TODO: check if this implementation is correct
    #For example, what's the right behavior for is_atom('+')
    def is_atom(self, parse_tree):
        #TODO: len==1 is wrong. For example, 123 should be an atom
        if not isinstance(parse_tree, (list, tuple)) and parse_tree in self.func_table:
            return False

        if len(parse_tree) == 1 and not isinstance(parse_tree[0], (list, tuple)):
            return True
        else:
            return False

    #TODO: how to handle single lists?
    def evaluate(self, parse_tree):
        if self.is_atom(parse_tree):
            return parse_tree[0]
        fn = parse_tree[0]
        if fn == 'cons':
            return [parse_tree[1]] + parse_tree[2]
        if fn == 'car':
            return self.evaluate(parse_tree[1][0])
        if fn == 'cdr':
            #TODO should we evaluate here?
            eval_sublist = self.evaluate(parse_tree[1])
            return eval_sublist[1:]
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
        """
        if fn[0] == 'lambda':
            value_names = fn[1]
            lambda_fn = fn[2]
            values = parse_tree[1:]

            #add values to dictionary
            for (value_name, value) in zip(value_names, values):
                self.func_table[value_name] = lambda none: self.evaluate(value)
            result = self.evaluate(lambda_fn)

            #clean up dictionary
            for value_name in value_names:
                del self.func_table[value_name]
            return result

            operation = parse_tree[2]
        """

        #handle anonymous functions specially, since they won't appear in self.func_table
        if fn[0] == 'lambda':
            args = [self.evaluate(x) for x in parse_tree[1:]]
            return self.evaluate(parse_tree[0]) (args)
        if fn not in self.func_table:
            #print fn
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
        self.assertEquals('1', result)

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
        self.assertEquals(interpreter.evaluate(interpreter.parse('a')[0]), '5')
        self.assertEquals(interpreter.evaluate(interpreter.parse('(+ a 2)')[0]), 7)

        interpreter.evaluate(interpreter.parse('(define b (+ a 1))')[0])
        self.assertEquals(interpreter.evaluate(interpreter.parse('b')[0]), 6)

        self.assertEquals(interpreter.evaluate(interpreter.parse('(+ a b)')[0]), 11)


    def test_lambda(self):
        interpreter = Interpreter()
        tree = interpreter.parse('((lambda (x) (* x x)) 4)')
        self.assertEquals(16, interpreter.evaluate(tree[0]))

        tree = interpreter.parse('(define square (lambda (x) (* x x)))')
        interpreter.evaluate(tree[0])
        self.assertEquals(25, interpreter.evaluate(interpreter.parse('(square 5)')[0]))
    
    def test_cond(self):
        pass

if __name__ == '__main__':
    unittest.main()


    interpreter = Interpreter()
    tree = interpreter.parse('(+ 1 1)')
    print interpreter.evaluate(tree[0])
    
