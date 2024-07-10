from lib.syntax.data import *
from lib.message import *

class MTSemanticAnalysis:
    def __init__(self, nodes: list[MTNode] = [], program: str = '', symbolTree: dict = {}, isLoopStatement = False) -> None:
        self.nodes: list[MTNode] = nodes
        self.program: str = program
        self.isLoopStatement: bool = isLoopStatement
        self.position = 0
        self.__symbolTree = {}
        self.__symbolTree.update(symbolTree)
    
    def analyze(self):
        while self.position < len(self.nodes):
            if (self.match(self.peek(), MTTokenType.IDENTIFIER)):
                self.parseIdentifier(self.peek())
                self.advance()
            elif self.match(self.peek(), MTTokenType.OPERATOR) or self.match(self.peek(), MTTokenType.CONDITIONAL_OPERATOR) or self.match(self.peek(), MTTokenType.LOGICAL_OPERATOR):
                self.evaluateExpression(self.peek())
                self.advance()
            elif self.match(self.peek(), MTTokenType.KEYWORD):
                self.parseKeyword(self.peek())
                self.advance()

        if self.peek() != None:
            MTCompilerMessage.error(f'Unexpected Node: {self.nodes[self.position].current.value}')
        
        return self.__symbolTree
    
    def parseIdentifier(self, node: MTNode):
        identifier: MTToken = self.consume(node, MTTokenType.IDENTIFIER).current
        
        if node.left != None:
            if identifier.value not in self.__symbolTree:
                self.__symbolTree[identifier.value] = self.consume(node.left, MTTokenType.KEYWORD, MTTokenSubType.DATA_TYPE_KEYWORDS).current.value
            else:
                MTCompilerMessage.semanticError(self.program, identifier, identifier.start_pos, f'Variable `{identifier.value}` is already defined')
        elif identifier.value not in self.__symbolTree:
            MTCompilerMessage.semanticError(self.program, identifier, identifier.start_pos, f'Undefined variable: `{identifier.value}`')
        
        if node.right != None:
            exp = self.evaluateExpression(node.right)
            if exp != self.__symbolTree[identifier.value]:
                MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'A value of type `{exp}` can\'t be assigned to a variable of type `{self.__symbolTree[identifier.value]}`')
    
    def parseKeyword(self, node: MTNode):
        if self.match(node, MTTokenType.KEYWORD, expected_value='print'):
            self.parsePrint(node)
        elif self.match(node, MTTokenType.KEYWORD, expected_value='pass'):
            pass
        elif (self.match(node, MTTokenType.KEYWORD, expected_value='continue') or self.match(node, MTTokenType.KEYWORD, expected_value='break')) and self.isLoopStatement:
            pass
        elif self.match(node, MTTokenType.KEYWORD, MTTokenSubType.CONDITIONAL_KEYWORDS):
            self.parseConditional(node)
        elif self.match(node, MTTokenType.KEYWORD, MTTokenSubType.LOOPS_KEYWORDS):
            self.parseLoop(node)
        else:
            MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Error while evaluating statement')
    
    def parsePrint(self, node: MTNode):
        if node.right != None:
            self.evaluateExpression(node.right)
        else:
            MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Error while evaluating statement')
    
    # Conditional Statements
    def parseConditional(self, node: MTNode):
        if self.match(node, MTTokenType.KEYWORD, MTTokenSubType.CONDITIONAL_KEYWORDS, expected_value='if'):
            self.parseConditionalIfElse(node)
        elif self.match(node, MTTokenType.KEYWORD, expected_value='switch'):
            self.parseConditionalSwitch(node)
        else:
            MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Error while evaluating statement')

    def parseConditionalIfElse(self, node: MTNode):
        if self.match(node, MTTokenType.KEYWORD, expected_value='if') or self.match(node, MTTokenType.KEYWORD, expected_value='elif'):
            exp = self.evaluateExpression(node.left)
            if exp != 'bool':
                MTCompilerMessage.semanticError(self.program, node.left.current, node.left.current.start_pos, f'`{exp}` is not a type of `bool`')

        MTSemanticAnalysis(node.statements, self.program, self.__symbolTree).analyze()

        if node.right != None:
            self.parseConditionalIfElse(node.right)
    
    def parseConditionalSwitch(self, node: MTNode):
        exp = self.evaluateExpression(node.left)

        for statement in node.statements:
            if self.match(statement, MTTokenType.KEYWORD, expected_value='case'):
                sexp = self.evaluateExpression(statement.left)
                if sexp != exp:
                    MTCompilerMessage.semanticError(self.program, statement.left.current, statement.left.current.start_pos, f'`{sexp}` is not a type of `{exp}`')
                MTSemanticAnalysis([statement.right], self.program, self.__symbolTree).analyze()
            elif self.match(statement, MTTokenType.KEYWORD, expected_value='default'):
                MTSemanticAnalysis([statement.right], self.program, self.__symbolTree).analyze()
    
    # Loops Statements
    def parseLoop(self, node: MTNode):
        if self.match(node, MTTokenType.KEYWORD, expected_value='for'):
            self.parseLoopFor(node)
        elif self.match(node, MTTokenType.KEYWORD, expected_value='while'):
            self.parseLoopWhile(node)
        elif self.match(node, MTTokenType.KEYWORD, expected_value='do'):
            self.parseLoopDoWhile(node)
        else:
            MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Error while evaluating statement')
    
    def parseLoopFor(self, node: MTNode):
        if node.left != None:
            self.consume(node.left, MTTokenType.LOOP_LOGIC)
            logic = node.left
            if len(logic.statements) == 3:
                tree = MTSemanticAnalysis(logic.statements, self.program).analyze()
                for var in tree:
                    if tree[var] != 'int':
                        MTCompilerMessage.semanticError(self.program, logic.current, logic.current.start_pos, f'Error while evaluating statement')
            else:
                MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Error while evaluating statement')
        else:
            MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Error while evaluating statement')
        
        newTree = {}
        newTree.update(self.__symbolTree)
        if tree != None:
            newTree.update(tree)
        tree = MTSemanticAnalysis(node.statements, self.program, newTree, isLoopStatement=True).analyze()

    def parseLoopWhile(self, node: MTNode, fromDoWhile = False):
        if node.left != None:
            exp = self.evaluateExpression(node.left)
            if exp != 'bool':
                MTCompilerMessage.semanticError(self.program, node.left.current, node.left.current.start_pos, f'`{exp}` is not a type of `bool`')
        else:
            MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Error while evaluating statement')
        
        if not fromDoWhile:
            tree = MTSemanticAnalysis(node.statements, self.program, self.__symbolTree, isLoopStatement=True).analyze()
    
    def parseLoopDoWhile(self, node: MTNode):
        if node.left != None:
            self.parseLoopWhile(node.left, True)
        else:
            MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Error while evaluating statement')

        tree = MTSemanticAnalysis(node.statements, self.program, self.__symbolTree, isLoopStatement=True).analyze()

    # Expression Evaluation
    def evaluateExpression(self, node: MTNode) -> str:
        if self.match(node, MTTokenType.VALUE):
            if node.current.sub_type == MTTokenSubType.NUMBER_VALUE:
                return 'int'
            elif node.current.sub_type == MTTokenSubType.DOUBLE_VALUE:
                return 'double'
            elif node.current.sub_type == MTTokenSubType.BOOLEAN_VALUE:
                return 'bool'
            elif node.current.sub_type == MTTokenSubType.STRING_VALUE:
                return 'str'
        elif self.match(node, MTTokenType.IDENTIFIER):
            if node.current.value in self.__symbolTree:
                return self.__symbolTree[node.current.value]
            else:
                MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'variable `{node.current.value}` is not defined')
        elif self.match(node, MTTokenType.OPERATOR):
            if node.current.value == '++' or node.current.value == '--':
                leftExp = self.evaluateExpression(node.left)

                if leftExp != 'int':
                    MTCompilerMessage.semanticError(self.program, node.left.current, node.left.current.start_pos, f'Error while evaluating expression')
                
                return 'int'
            
            leftExp = self.evaluateExpression(node.left)
            rightExp = self.evaluateExpression(node.right)
            
            if leftExp == 'bool':
                MTCompilerMessage.semanticError(self.program, node.left.current, node.left.current.start_pos, f'Error while evaluating expression')
            elif rightExp == 'bool':
                MTCompilerMessage.semanticError(self.program, node.left.current, node.left.current.start_pos, f'Error while evaluating expression')

            if (node.current.value == '*' or node.current.value == '+') and (leftExp == 'str' or rightExp == 'str'):
                if node.current.value == '*' and ((leftExp == 'str' and rightExp == 'int') or (rightExp == 'str' and leftExp == 'int')):
                    return 'str'
                elif node.current.value == '+' and leftExp == 'str' and rightExp == 'str':
                    return 'str'
            elif (leftExp != 'str' and rightExp != 'str') and leftExp == rightExp:
                return leftExp
            elif (leftExp == 'double' and rightExp == 'int') or (leftExp == 'int' and rightExp == 'double'):
                return 'double'

            MTCompilerMessage.semanticError(self.program, node.left.current, node.left.current.start_pos, f'Error while evaluating expression')
        elif self.match(node, MTTokenType.CONDITIONAL_OPERATOR):
            if node.current.value == '?':
                leftExp = self.evaluateExpression(node.left)
                if leftExp != 'bool':
                    MTCompilerMessage.semanticError(self.program, node.left.current, node.left.current.start_pos, f'`{leftExp}` is not a type of `bool`')
                
                self.consume(node.right, MTTokenType.CONDITIONAL_OPERATOR, expected_value=':')
                currentNode = node.right
                leftExp = self.evaluateExpression(currentNode.left)
                rightExp = self.evaluateExpression(currentNode.right)
                if leftExp != rightExp:
                    MTCompilerMessage.semanticError(self.program, currentNode.left.current, currentNode.left.current.start_pos, f'Error while evaluating expression')
                return leftExp

            leftExp = self.evaluateExpression(node.left)
            rightExp = self.evaluateExpression(node.right)

            if leftExp == rightExp:
                return 'bool'

            MTCompilerMessage.semanticError(self.program, node.left.current, node.left.current.start_pos, f'Error while evaluating expression')
        elif self.match(node, MTTokenType.LOGICAL_OPERATOR):
            leftExp = self.evaluateExpression(node.left)
            rightExp = self.evaluateExpression(node.right)
            
            if leftExp == 'bool' and rightExp == 'bool':
                return 'bool'
            elif leftExp != 'bool':
                MTCompilerMessage.semanticError(self.program, node.left.current, node.left.current.start_pos, f'`{leftExp}` is not a type of `bool`')
            elif rightExp != 'bool':
                MTCompilerMessage.semanticError(self.program, node.right.current, node.right.current.start_pos, f'`{rightExp}` is not a type of `bool`')
            
            MTCompilerMessage.semanticError(self.program, node.left.current, node.left.current.start_pos, f'Error while evaluating expression')
        else:
            MTCompilerMessage.semanticError(self.program, node.current, node.current.start_pos, f'Error while evaluating expression')

    # Core Functions
    def consume(self, node: MTNode, expected_type: MTTokenType, expected_sub_type: MTTokenSubType = MTTokenSubType.NONE, expected_value: str = None):
        if self.match(node, expected_type, expected_sub_type, expected_value):
            return node
        MTCompilerMessage.error(f'TypeError: Unexpected Node : {node.current.value}')

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