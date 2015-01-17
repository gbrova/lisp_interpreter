import unittest
import interpreter as LispInterpreter

class TestInterpreter(unittest.TestCase):
    def test_parse(self):
        interpreter = LispInterpreter.LispInterpreter()
        result = interpreter.parse('(+ 1 (- 1 2))')
        self.assertEquals([['+', '1', ['-', '1', '2']]], result)

    def test_isAtom(self):
        interpreter = LispInterpreter.LispInterpreter()
        tree = interpreter.parse('(+ 1 1)')
        self.assertFalse(interpreter.is_atom(tree))
        self.assertFalse(interpreter.is_atom(tree[0]))
        self.assertTrue(interpreter.is_atom(tree[0][1]))

    def test_evaluate(self):
        interpreter = LispInterpreter.LispInterpreter()

        tree1 = interpreter.parse('(+ 1 1)')
        self.assertEquals(2, interpreter.evaluate(tree1[0]))

        tree2 = interpreter.parse('(+ 1 (* 3 2))')
        self.assertEquals(7, interpreter.evaluate(tree2[0]))

    def test_eq(self):
        interpreter = LispInterpreter.LispInterpreter()
        tree1 = interpreter.parse('(eq? 1 1)')
        self.assertTrue(interpreter.evaluate(tree1[0]))

        tree2 = interpreter.parse('(eq? 1 2)')
        self.assertFalse(interpreter.evaluate(tree2[0]))

    def test_cons(self):
        interpreter = LispInterpreter.LispInterpreter()
        tree = interpreter.parse('(cons 1 (2 3))')
        result = interpreter.evaluate(tree[0])
        self.assertEquals(['1', '2', '3'], result)

    def test_car(self):
        interpreter = LispInterpreter.LispInterpreter()
        tree = interpreter.parse('(car (1 2 3))')
        result = interpreter.evaluate(tree[0])
        self.assertEquals(1, result)

    """
    def test_cdr(self):
        interpreter = LispInterpreter.LispInterpreter()
        tree = interpreter.parse('(cdr (1 2 3))')
        result = interpreter.evaluate(tree[0])
        self.assertEquals(['2', '3'], result)

        tree = interpreter.parse('(cdr (cdr (1 2 3)))')
        result = interpreter.evaluate(tree[0])
        self.assertEquals(['3'], result)

        tree = interpreter.parse('(cdr (cdr (cdr (1 2 3))))')
        result = interpreter.evaluate(tree[0])
        self.assertEquals([], result)
    """
    
    def test_define(self):
        interpreter = LispInterpreter.LispInterpreter()
        tree = interpreter.parse('(define a 5)')
        interpreter.evaluate(tree[0])
        self.assertEquals(interpreter.evaluate(interpreter.parse('a')[0]), 5)
        self.assertEquals(interpreter.evaluate(interpreter.parse('(+ a 2)')[0]), 7)

        interpreter.evaluate(interpreter.parse('(define b (+ a 1))')[0])
        self.assertEquals(interpreter.evaluate(interpreter.parse('b')[0]), 6)

        self.assertEquals(interpreter.evaluate(interpreter.parse('(+ a b)')[0]), 11)



    def test_lambda(self):
        interpreter = LispInterpreter.LispInterpreter()
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
        interpreter = LispInterpreter.LispInterpreter()
        tree = interpreter.parse('(quote a)')
        self.assertEquals('a', interpreter.evaluate(tree[0]))

        # TODO this might not be the desired behavior
        tree = interpreter.parse('(quote (1 2 3))')
        self.assertEquals("['1', '2', '3']", interpreter.evaluate(tree[0]))

    def test_cond(self):
        interpreter = LispInterpreter.LispInterpreter()
        tree = interpreter.parse('(cond ((eq? 1 2) 1) ((eq? 2 2) 2) (else 3))')
        self.assertEquals(2, interpreter.evaluate(tree[0]))

        tree = interpreter.parse('(cond ((eq? 1 2) 1) ((eq? 1 2) 2) (else 3))')
        self.assertEquals(3, interpreter.evaluate(tree[0]))

    def test_recursion(self):
        interpreter = LispInterpreter.LispInterpreter()
        tree = interpreter.parse('(define sumall (lambda (x) (cond ((eq? x 0) 0) (else (+ x (sumall (- x 1)) )))))')
        interpreter.evaluate(tree[0])
        tree = interpreter.parse('(sumall 10)')
        self.assertEquals(55, interpreter.evaluate(tree[0]))

if __name__ == '__main__':
    unittest.main()
