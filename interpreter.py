import re
import collections

class LispInterpreter:
    def __init__(self):
        func_table = collections.defaultdict(lambda: None)
        func_table['+'] = lambda l: int(l[0]) + int(l[1])
        func_table['-'] = lambda l: int(l[0]) - int(l[1])
        func_table['*'] = lambda l: int(l[0]) * int(l[1])
        func_table['/'] = lambda l: int(l[0]) / int(l[1])
        func_table['eq?'] = lambda l: l[0] == l[1]

        # hacky way of storing previous values
        self.func_table_stack = collections.defaultdict(list)
        
        self.func_table = func_table
        
    def parse(self, expr):
        obj_stack = [[]]
        #TODO: is it faster to use replace instead of re.split()? 
        #expr_tokens = expr.replace('(', ' ( ').replace(')', ' ) ').split(' ')
        
        # Split on the characters space, (, and ).
        # Include the match as part of the resulting list
        expr_tokens = re.split('([ \'()])', expr)
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
            if value in self.func_table:
                return self.evaluate(self.func_table[value])
            try:
                int(value)
                return int(value)
            except ValueError:
                return self.func_table[value]
            except:
                return value
        fn = parse_tree[0]
        if fn == 'quote':
            # TODO this isn't quite right, because the syntax might be changed somewhat
            return ' '.join([str(item) for item in parse_tree[1:]])
        if fn == 'cons':
            return [parse_tree[1]] + parse_tree[2]
        if fn == 'car':
            return self.evaluate(parse_tree[1][0])
        if fn == 'cdr':
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
            self.func_table[parse_tree[1]] = parse_tree[2]
            return None
        if fn == 'lambda':
            def cur_fn(values):
                value_names = parse_tree[1]
                lambda_fn = parse_tree[2]
                for (value_name, value) in zip(value_names, values):
                    self.func_table_stack[value_name].append(self.func_table[value_name])
                    self.func_table[value_name] = self.evaluate(value)
                result = self.evaluate(lambda_fn)
                for value_name in value_names:
                    del self.func_table[value_name]
                    self.func_table[value_name] = self.func_table_stack[value_name].pop()
                return result
            return cur_fn

        #handle anonymous functions specially, since they won't appear in self.func_table
        if fn[0] == 'lambda':
            args = [self.evaluate(x) for x in parse_tree[1:]]
            #func = self.evaluate(parse_tree[0])
            func = parse_tree[0]
            return self.evaluate(func) (args)
#        if fn not in self.func_table:
#            print 'shouldnt be here', parse_tree
            #TODO: this is hacky, just to get lists to work without '. Remove later. 
#            return parse_tree

        else:
            # apply function to everything else in the list
            args = [self.evaluate(x) for x in parse_tree[1:]]
            cur_symbol = self.evaluate(self.func_table[parse_tree[0]])
            if callable(cur_symbol):
                return self.evaluate(cur_symbol(args))
            else:
                return self.evaluate(cur_symbol)


def repl(prompt):
    #read-eval-print loop
    interpreter = LispInterpreter()
    while True:
        line = raw_input(prompt)
        tree = interpreter.parse(line)
        if len(tree) != 1:
            continue
        result = interpreter.evaluate(tree[0])
        if result is not None:
            print result
    
if __name__ == '__main__':
    repl('mylisp> ')

"""
to test: 
(define fact (lambda (x) (if (eq? x 1) (1) else (* x (fact (- x 1))) ))


#recursion
(define test (lambda (x) (cond ((eq? x 1) 1) (else (test (- x 1))))))

(define sumall (lambda (x) (cond ((eq? x 0) 0) (else (+ x (sumall (- x 1)) )))))
"""
    
