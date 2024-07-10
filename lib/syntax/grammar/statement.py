from lib.syntax.grammar.expression import *
from lib.lexer.token_class import *
from lib.message import MTCompilerMessage
from lib.syntax.grammar.expression import MTExpressionGrammar

class MTStatementGrammar:
    def __init__(self, tokens: list[MTToken], program: str, position: int, endChar: str = ';') -> None:
        self.tokens = tokens
        self.position = position
        self.program = program
        self.endChar = endChar
    
    # entry point for the statement parsing
    def generateStatement(self) -> MTNode:
        while self.tokens[self.position].value != self.endChar:
            
            if self.match(MTTokenType.KEYWORD, MTTokenSubType.DATA_TYPE_KEYWORDS):
                node = self.parseDataType()
                return self.position, node
            elif self.match(MTTokenType.KEYWORD, expected_value='print'):
                node = self.parsePrint()
                return self.position, node
            elif self.match(MTTokenType.KEYWORD, expected_value='continue') or self.match(MTTokenType.KEYWORD, expected_value='break') or self.match(MTTokenType.KEYWORD, expected_value='pass'):
                node = MTNode(self.consume(MTTokenType.KEYWORD))
                return self.position, node
            elif self.match(MTTokenType.IDENTIFIER):
                node = self.parseIdentifier()
                return self.position, node
            elif self.match(MTTokenType.KEYWORD, MTTokenSubType.CONDITIONAL_KEYWORDS):
                node = self.parseConditionalStatement()
                return self.position, node
            elif self.match(MTTokenType.KEYWORD, MTTokenSubType.LOOPS_KEYWORDS):
                node = self.parseLoopStatement()
                return self.position, node
            else:
                MTCompilerMessage.syntaxError(self.program, self.peek(), self.peek().start_pos)

        if self.peek() != None:
            MTCompilerMessage.syntaxError(self.program, self.peek(), self.peek().start_pos)
    
    def parseDataType(self) -> MTNode:
        node = MTNode(self.consume(MTTokenType.KEYWORD, MTTokenSubType.DATA_TYPE_KEYWORDS))
        id = self.parseIdentifier()
        id.left = node
        node = id
        return node
    
    def parseIdentifier(self) -> MTNode:
        node = MTNode(self.consume(MTTokenType.IDENTIFIER))

        if self.match(MTTokenType.OPERATOR, expected_value='='):
            self.advance()
            node.right = self.parseExpressions()
        elif self.match(MTTokenType.OPERATOR):
            self.position, exp = MTExpressionGrammar(self.tokens, self.program, self.position - 1, self.endChar).generateExpression()
            exp.left = node
            node = exp

        return node
    
    def parseExpressions(self) -> MTNode:
        self.position, node = MTExpressionGrammar(self.tokens, self.program, self.position, self.endChar).generateExpression()
        return node
    
    def parsePrint(self) -> MTNode:
        node = MTNode(self.consume(MTTokenType.KEYWORD, expected_value='print'))

        self.consume(MTTokenType.SEPARATOR, expected_value='(')
        self.position, node.right = MTExpressionGrammar(self.tokens, self.program, self.position, ')').generateExpression()
        self.consume(MTTokenType.SEPARATOR, expected_value=')')

        return node
    
    # For Conditional
    def parseConditionalStatement(self) -> MTNode:
        if self.match(MTTokenType.KEYWORD, MTTokenSubType.CONDITIONAL_KEYWORDS, 'if'):
            return self.parseConditionalIfElse()
        elif self.match(MTTokenType.KEYWORD, MTTokenSubType.CONDITIONAL_KEYWORDS, 'switch'):
            return self.parseConditionalSwitch()
        else:
            MTCompilerMessage.syntaxError(self.program, self.peek(), self.peek().start_pos)
    
    def parseConditionalIfElse(self) -> MTNode:
        if self.match(MTTokenType.KEYWORD, MTTokenSubType.CONDITIONAL_KEYWORDS, 'if'):
            node = MTNode(self.consume(MTTokenType.KEYWORD, MTTokenSubType.CONDITIONAL_KEYWORDS, 'if'))
        elif self.match(MTTokenType.KEYWORD, MTTokenSubType.CONDITIONAL_KEYWORDS, 'elif'):
            node = MTNode(self.consume(MTTokenType.KEYWORD, MTTokenSubType.CONDITIONAL_KEYWORDS, 'elif'))
        else:
            node = MTNode(self.consume(MTTokenType.KEYWORD, MTTokenSubType.CONDITIONAL_KEYWORDS, 'else'))
        
        if node.current.value == 'if' or node.current.value == 'elif':
            self.consume(MTTokenType.SEPARATOR, expected_value='(')
            self.position, node.left = MTExpressionGrammar(self.tokens, self.program, self.position, ')').generateExpression()
            self.consume(MTTokenType.SEPARATOR, expected_value=')')
        
        self.consume(MTTokenType.SEPARATOR, expected_value='{')
        while not self.match(MTTokenType.SEPARATOR, expected_value='}'):
            self.position, statement = MTStatementGrammar(self.tokens, self.program, self.position).generateStatement()
            if self.previous().value != '}':
                self.consume(MTTokenType.SEPARATOR, expected_value=';')
            node.statements.append(statement)
        self.consume(MTTokenType.SEPARATOR, expected_value='}')

        if self.match(MTTokenType.KEYWORD, expected_value='elif') or self.match(MTTokenType.KEYWORD, expected_value='else'):
            node.right = self.parseConditionalIfElse()
        
        return node
    
    def parseConditionalSwitch(self) -> MTNode:
        node = MTNode(self.consume(MTTokenType.KEYWORD, MTTokenSubType.CONDITIONAL_KEYWORDS, 'switch'))

        self.consume(MTTokenType.SEPARATOR, expected_value='(')
        self.position, node.left = MTExpressionGrammar(self.tokens, self.program, self.position, ')').generateExpression()
        self.consume(MTTokenType.SEPARATOR, expected_value=')')

        self.consume(MTTokenType.SEPARATOR, expected_value='{')

        while self.match(MTTokenType.KEYWORD, MTTokenSubType.CONDITIONAL_KEYWORDS, expected_value='case'):
            caseStatement = MTNode(self.consume(MTTokenType.KEYWORD, MTTokenSubType.CONDITIONAL_KEYWORDS, expected_value='case'))

            if self.match(MTTokenType.VALUE):
                caseStatement.left = MTNode(self.consume(MTTokenType.VALUE))
            elif self.match(MTTokenType.IDENTIFIER):
                caseStatement.left = MTNode(self.consume(MTTokenType.IDENTIFIER))

            self.consume(MTTokenType.CONDITIONAL_OPERATOR, expected_value=':')
            self.position, caseStatement.right = MTStatementGrammar(self.tokens, self.program, self.position).generateStatement()
            self.consume(MTTokenType.SEPARATOR, expected_value=';')
            
            if self.match(MTTokenType.KEYWORD, expected_value='break'):
                self.consume(MTTokenType.KEYWORD, expected_value='break')
                self.consume(MTTokenType.SEPARATOR, expected_value=';')
            
            node.statements.append(caseStatement)
        
        # for default statement
        if self.match(MTTokenType.KEYWORD, MTTokenSubType.CONDITIONAL_KEYWORDS, expected_value='default'):
            defaultStatement = MTNode(self.consume(MTTokenType.KEYWORD, MTTokenSubType.CONDITIONAL_KEYWORDS, expected_value='default'))
            self.consume(MTTokenType.CONDITIONAL_OPERATOR, expected_value=':')
            self.position, defaultStatement.right = MTStatementGrammar(self.tokens, self.program, self.position).generateStatement()
            self.consume(MTTokenType.SEPARATOR, expected_value=';')
            node.statements.append(defaultStatement)
        
        self.consume(MTTokenType.SEPARATOR, expected_value='}')
        
        return node

    # For loops
    def parseLoopStatement(self):
        if self.match(MTTokenType.KEYWORD, MTTokenSubType.LOOPS_KEYWORDS, 'for'):
            return self.parseForLoop()
        elif self.match(MTTokenType.KEYWORD, MTTokenSubType.LOOPS_KEYWORDS, 'while'):
            return self.parseWhileLoop()
        elif self.match(MTTokenType.KEYWORD, MTTokenSubType.LOOPS_KEYWORDS, 'do'):
            return self.parseDoWhileLoop()
        else:
            MTCompilerMessage.syntaxError(self.program, self.peek(), self.peek().start_pos)

    def parseForLoop(self):
        node = MTNode(self.consume(MTTokenType.KEYWORD, MTTokenSubType.LOOPS_KEYWORDS, 'for'))
        logic = MTNode(MTToken(MTTokenType.LOOP_LOGIC, '', 0, 0))

        self.consume(MTTokenType.SEPARATOR, expected_value='(')
        # self.parseDataType()
        logic.statements.append(self.parseDataType())
        self.consume(MTTokenType.SEPARATOR, expected_value=';')
        self.position, cond = MTExpressionGrammar(self.tokens, self.program, self.position).generateExpression()
        logic.statements.append(cond)
        self.consume(MTTokenType.SEPARATOR, expected_value=';')
        self.position, inc = MTExpressionGrammar(self.tokens, self.program, self.position, ')').generateExpression()
        logic.statements.append(inc)
        self.consume(MTTokenType.SEPARATOR, expected_value=')')

        node.left = logic
        # print(node)
        # exit(1)
        
        self.consume(MTTokenType.SEPARATOR, expected_value='{')
        while not self.match(MTTokenType.SEPARATOR, expected_value='}'):
            self.position, statement = MTStatementGrammar(self.tokens, self.program, self.position).generateStatement()
            if self.previous().value != '}':
                self.consume(MTTokenType.SEPARATOR, expected_value=';')
            node.statements.append(statement)
        self.consume(MTTokenType.SEPARATOR, expected_value='}')

        return node
    
    def parseWhileLoop(self, fromDoWhile = False) -> MTNode:
        node = MTNode(self.consume(MTTokenType.KEYWORD, MTTokenSubType.LOOPS_KEYWORDS, expected_value='while'))

        self.consume(MTTokenType.SEPARATOR, expected_value='(')
        self.position, node.left = MTExpressionGrammar(self.tokens, self.program, self.position, ')').generateExpression()
        self.consume(MTTokenType.SEPARATOR, expected_value=')')

        if fromDoWhile:
            self.consume(MTTokenType.SEPARATOR, expected_value=';')
        else:
            self.consume(MTTokenType.SEPARATOR, expected_value='{')
            while not self.match(MTTokenType.SEPARATOR, expected_value='}'):
                self.position, statement = MTStatementGrammar(self.tokens, self.program, self.position).generateStatement()
                if self.previous().value != '}':
                    self.consume(MTTokenType.SEPARATOR, expected_value=';')
                node.statements.append(statement)
            self.consume(MTTokenType.SEPARATOR, expected_value='}')

        return node
    
    def parseDoWhileLoop(self) -> MTNode:
        node = MTNode(self.consume(MTTokenType.KEYWORD, MTTokenSubType.LOOPS_KEYWORDS, expected_value='do'))

        self.consume(MTTokenType.SEPARATOR, expected_value='{')
        while not self.match(MTTokenType.SEPARATOR, expected_value='}'):
            self.position, statement = MTStatementGrammar(self.tokens, self.program, self.position).generateStatement()
            if self.previous().value != '}':
                self.consume(MTTokenType.SEPARATOR, expected_value=';')
            node.statements.append(statement)
        self.consume(MTTokenType.SEPARATOR, expected_value='}')

        node.left = self.parseWhileLoop(True)

        return node

    # Core Functions
    def match(self, expected_type: MTTokenType, expected_sub_type: MTTokenSubType = MTTokenSubType.NONE, expected_value: str = None) -> bool:
        if self.check(expected_type, expected_sub_type=expected_sub_type, expected_value=expected_value):
            return True
        return False
    
    def consume(self, expected_type: MTTokenType, expected_sub_type: MTTokenSubType = MTTokenSubType.NONE, expected_value: str = None):
        if self.check(expected_type=expected_type, expected_sub_type=expected_sub_type, expected_value=expected_value):
            return self.advance()
        MTCompilerMessage.syntaxError(self.program, self.peek(), self.peek().start_pos, expected='' if expected_value == None else expected_value)
    
    def expect(self, expected_type: MTTokenType, expected_sub_type: MTTokenSubType = MTTokenSubType.NONE, expected_value: str = None):
        if self.check(expected_type=expected_type, expected_sub_type=expected_sub_type, expected_value=expected_value):
            return True
        MTCompilerMessage.syntaxError(self.program, self.peek(), self.peek().start_pos, expected='' if expected_value == None else expected_value)
    
    def check(self, expected_type: MTTokenType, expected_sub_type: MTTokenSubType = MTTokenSubType.NONE, expected_value: str = None):
        if self.is_at_end():
            return False
        return self.peek().type == expected_type and (expected_sub_type == MTTokenSubType.NONE or self.peek().sub_type == expected_sub_type) and (expected_value == None or self.tokens[self.position].value == expected_value)
    
    def advance(self):
        if not self.is_at_end():
            self.position += 1
        return self.previous()

    def previous(self):
        return self.tokens[self.position - 1]
    
    def peek(self):
        if self.is_at_end():
            return None
        return self.tokens[self.position]

    def is_at_end(self) -> bool:
        return self.position >= len(self.tokens)