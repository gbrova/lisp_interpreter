import re

class Interpreter: 
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
        if len(parse_tree) == 1 and not isinstance(parse_tree[0], (list, tuple)):
            return True
        else:
            return False

    #TODO: how to handle single lists?
    def evaluate(self, parse_tree, func_table):
        # apply function to everything else in the list
        if self.is_atom(parse_tree):
            return parse_tree[0]
        else:
            args = [self.evaluate(x, func_table) for x in parse_tree[1:]]
            return func_table[parse_tree[0]] (args)


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
        func_table = {}
        func_table['+'] = lambda l: int(l[0]) + int(l[1])
        func_table['-'] = lambda l: int(l[0]) - int(l[1])
        func_table['*'] = lambda l: int(l[0]) * int(l[1])
        func_table['/'] = lambda l: int(l[0]) / int(l[1])

        tree1 = interpreter.parse('(+ 1 1)')
        self.assertEquals(2, interpreter.evaluate(tree1[0], func_table))

        tree2 = interpreter.parse('(+ 1 (* 3 2))')
        self.assertEquals(7, interpreter.evaluate(tree2[0], func_table))



if __name__ == '__main__':
    unittest.main()


    interpreter = Interpreter()
    tree = interpreter.parse('(+ 1 1)')
    print interpreter.evaluate(tree[0], func_table)
    
