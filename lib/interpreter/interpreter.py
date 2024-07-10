from lib.syntax.data import *
from lib.lexer.token_class import *
from lib.message import *

class MTInterpreter:
    def __init__(self, nodes: list[MTNode], program: str, symbolTree: dict = {}, valueTree: dict = {}, isLoopStatement = False) -> None:
        self.nodes: list[MTNode] = nodes
        self.program: str = program
        self.isLoopStatement: bool = isLoopStatement
        self.position = 0
        self.__symbolTree = {}
        self.__valueTree = {}
        self.__symbolTree.update(symbolTree)
        self.__valueTree.update(valueTree)
    
    def interpret(self):
        while self.position < len(self.nodes):
            if self.match(self.peek(), MTTokenType.IDENTIFIER):
                self.interpretIdentifier(self.peek())
                self.advance()
            elif self.match(self.peek(), MTTokenType.KEYWORD):
                self.interpretKeyword(self.peek())
                self.advance()
            elif self.match(self.peek(), MTTokenType.OPERATOR) or self.match(self.peek(), MTTokenType.CONDITIONAL_OPERATOR) or self.match(self.peek(), MTTokenType.LOGICAL_OPERATOR):
                self.interpretExpression(self.peek())
                self.advance()
            else:
                MTCompilerMessage.semanticError(self.program, self.peek().current, self.peek().current.start_pos, f'Unexpected Node: {self.nodes[self.position].current.value}')

        if self.peek() != None:
            MTCompilerMessage.semanticError(self.program, self.peek().current, self.peek().current.start_pos, f'Unexpected Node: {self.nodes[self.position].current.value}')

        return {
            'symbol_tree': self.__symbolTree,
            'value_tree': self.__valueTree,
        }
    
    # Functions
    def interpretKeyword(self, node: MTNode):
        if self.match(node, MTTokenType.KEYWORD, expected_value='print'):
            self.interpretPrint(node)
        elif self.match(node, MTTokenType.KEYWORD, expected_value='pass'):
            pass
        elif self.match(node, MTTokenType.KEYWORD, MTTokenSubType.CONDITIONAL_KEYWORDS):
            self.interpretCondition(node)
        elif self.match(node, MTTokenType.KEYWORD, MTTokenSubType.LOOPS_KEYWORDS):
            self.interpretLoop(node)
        else:
            MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Unexpected Node: {self.nodes[self.position].current.value}')

    def interpretPrint(self, node: MTNode):
        exp = self.interpretExpression(node.right)
        if exp != None:
            if type(exp) is bool:
                exp = 'true' if exp else 'false'
        else:
            exp = 'null'
        print(exp)

    def interpretIdentifier(self, node: MTNode):
        if node.left != None and node.current.value not in self.__symbolTree:
            self.__symbolTree[node.current.value] = node.left.current.value
            if node.right != None:
                exp = self.interpretExpression(node.right)
                self.__valueTree[node.current.value] = exp
        elif node.left == None and node.current.value in self.__symbolTree:
            if node.right != None:
                exp = self.interpretExpression(node.right)
                self.__valueTree[node.current.value] = exp
        else:
            MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Undefined variable: `{node.current.value}`')
    
    # Conditional
    def interpretCondition(self, node: MTNode):
        if self.match(node, MTTokenType.KEYWORD, expected_value='if'):
            self.interpretConditionIfElse(node)
        elif self.match(node, MTTokenType.KEYWORD, expected_value='switch'):
            self.interpretConditionSwitch(node)
        else:
            MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Unexpected Node: {self.nodes[self.position].current.value}')
    
    def interpretConditionIfElse(self, node: MTNode):
        exp = True
        if (node.current.value == 'if' or node.current.value == 'elif') and node.left != None:
            exp = self.interpretExpression(node.left)
        elif node.current.value != 'else':
            MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Error while evaluating expression')
        
        if type(exp) is bool:
            if exp:
                data = MTInterpreter(node.statements, self.program, self.__symbolTree, self.__valueTree).interpret()
                for v in data['value_tree']:
                    if v in self.__valueTree:
                        self.__valueTree[v] = data['value_tree'][v]
            elif node.right != None:
                self.interpretConditionIfElse(node.right)
        else:
            MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Expression should be type of `bool`')
    
    def interpretConditionSwitch(self, node: MTNode):
        exp = self.interpretExpression(node.left)
        
        for statement in node.statements:
            if self.match(statement, MTTokenType.KEYWORD, expected_value='case'):
                leftExp = self.interpretExpression(statement.left)
                if leftExp == exp:
                    data = MTInterpreter([statement.right], self.program, self.__symbolTree, self.__valueTree).interpret()
                    for v in data['value_tree']:
                        if v in self.__valueTree:
                            self.__valueTree[v] = data['value_tree'][v]
                    break
            elif self.match(statement, MTTokenType.KEYWORD, expected_value='default'):
                data = MTInterpreter([statement.right], self.program, self.__symbolTree, self.__valueTree).interpret()
                for v in data['value_tree']:
                    if v in self.__valueTree:
                        self.__valueTree[v] = data['value_tree'][v]
                break
            else:
                MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Invalid case')

    # Loops
    def interpretLoop(self, node: MTNode):
        if self.match(node, MTTokenType.KEYWORD, expected_value='for'):
            self.interpretForLoop(node)
        elif self.match(node, MTTokenType.KEYWORD, expected_value='while'):
            self.interpretWhileLoop(node)
        elif self.match(node, MTTokenType.KEYWORD, expected_value='do'):
            self.interpretDoWhileLoop(node)
        else:
            MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Unexpected Node: {self.nodes[self.position].current.value}')
    
    def interpretForLoop(self, node: MTNode):
        if node.left != None:
            logic = node.left
            if len(logic.statements) == 3:
                tree = MTInterpreter([logic.statements[0]], self.program).interpret()

                self.__symbolTree.update(tree['symbol_tree'])
                self.__valueTree.update(tree['value_tree'])

                exp = self.interpretExpression(logic.statements[1])
                while type(exp) is bool and exp:
                    data = MTInterpreter(node.statements, self.program, self.__symbolTree, self.__valueTree).interpret()
                    for v in data['value_tree']:
                        if v in self.__valueTree:
                            self.__valueTree[v] = data['value_tree'][v]
                    
                    self.interpretExpression(logic.statements[2])
                    exp = self.interpretExpression(logic.statements[1])
                
                for i in tree['symbol_tree']:
                    del self.__symbolTree[i]
                for i in tree['value_tree']:
                    del self.__valueTree[i]
            else:
                MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Error while evaluating statement')
        else:
            MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Error while evaluating statement')
        pass

    def interpretWhileLoop(self, node: MTNode):
        if node.left != None:
            exp = self.interpretExpression(node.left)
            while type(exp) is bool and exp:
                data = MTInterpreter(node.statements, self.program, self.__symbolTree, self.__valueTree).interpret()
                for v in data['value_tree']:
                    if v in self.__valueTree:
                        self.__valueTree[v] = data['value_tree'][v]
                exp = self.interpretExpression(node.left)
        else:
            MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Error while evaluating statement')
    
    def interpretDoWhileLoop(self, node: MTNode):
        exp = True
        while type(exp) is bool and exp:
            data = MTInterpreter(node.statements, self.program, self.__symbolTree, self.__valueTree).interpret()
            for v in data['value_tree']:
                if v in self.__valueTree:
                    self.__valueTree[v] = data['value_tree'][v]
            exp = self.interpretExpression(node.left.left)

    # Expression
    def interpretExpression(self, node: MTNode):
        if self.match(node, MTTokenType.IDENTIFIER):
            if node.current.value in self.__valueTree:
                return self.__valueTree[node.current.value]
        elif self.match(node, MTTokenType.VALUE):
            if node.current.sub_type == MTTokenSubType.NUMBER_VALUE:
                return int(node.current.value)
            elif node.current.sub_type == MTTokenSubType.STRING_VALUE:
                return str(node.current.value)
            elif node.current.sub_type == MTTokenSubType.BOOLEAN_VALUE:
                return True if node.current.value == 'true' else False
            elif node.current.sub_type == MTTokenSubType.DOUBLE_VALUE:
                return float(node.current.value)
            else:
                MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Value type is not supported')
        elif self.match(node, MTTokenType.OPERATOR):
            if node.current.value == '++' or node.current.value == '--':
                exp = self.interpretExpression(node.left)
                if node.current.value == '++':
                    self.__valueTree[node.left.current.value] = exp + 1
                    return exp
                elif node.current.value == '--':
                    self.__valueTree[node.left.current.value] = exp - 1
                    return exp

            leftExp = self.interpretExpression(node.left)
            rightExp = self.interpretExpression(node.right)
            
            if node.current.value == '+':
                return leftExp + rightExp
            elif node.current.value == '-':
                return leftExp - rightExp
            elif node.current.value == '*':
                return leftExp * rightExp
            elif node.current.value == '/':
                return leftExp / rightExp
            else:
                MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Arithmentic operation not supported')
        elif self.match(node, MTTokenType.CONDITIONAL_OPERATOR):
            if node.current.value == '?' and node.left != None:
                exp = self.interpretExpression(node.left)
                
                if type(exp) != bool:
                    MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Error while evaluating expression')
                elif node.right != None:
                    subNode = node.right
                    leftExp = self.interpretExpression(subNode.left)
                    rightExp = self.interpretExpression(subNode.right)
                    return leftExp if exp else rightExp
                else:
                    MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Error while evaluating expression')
            
            leftExp = self.interpretExpression(node.left)
            rightExp = self.interpretExpression(node.right)

            if node.current.value == '<':
                return leftExp < rightExp
            elif node.current.value == '>':
                return leftExp > rightExp
            elif node.current.value == '==':
                return leftExp == rightExp
            elif node.current.value == '<=':
                return leftExp <= rightExp
            elif node.current.value == '>=':
                return leftExp >= rightExp
            else:
                MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Conditional operation not supported')
        elif self.match(node, MTTokenType.LOGICAL_OPERATOR):
            leftExp = self.interpretExpression(node.left)
            rightExp = self.interpretExpression(node.right)

            if node.current.value == '&&':
                return leftExp and rightExp
            elif node.current.value == '||':
                return leftExp or rightExp
            else:
                MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Conditional operation not supported')
        else:
            MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Error while evaluating expression')
    
    # Core Functions
    def consume(self, node: MTNode, expected_type: MTTokenType, expected_sub_type: MTTokenSubType = MTTokenSubType.NONE, expected_value: str = None):
        if self.match(node, expected_type, expected_sub_type, expected_value):
            return node
        MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'TypeError: Unexpected Node : {node.current.value}')

    def match(self, node: MTNode, expected_type: MTTokenType, expected_sub_type: MTTokenSubType = MTTokenSubType.NONE, expected_value: str = None):
        if self.is_at_end():
            return False
        return node.current.type == expected_type and (expected_sub_type == MTTokenSubType.NONE or node.current.sub_type == expected_sub_type) and (expected_value == None or node.current.value == expected_value)

    def peek(self):
        if not self.is_at_end():
            return self.nodes[self.position]
        return None
    
    def advance(self):
        if not self.is_at_end():
            self.position += 1

    def is_at_end(self):
        return self.position >= len(self.nodes)