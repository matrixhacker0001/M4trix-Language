from lib.lexer.token_class import *
from lib.message import MTCompilerMessage
from lib.syntax.data import *

class MTExpressionGrammar:
    def __init__(self, tokens: list[MTToken], program: str, position: int, endChar: str = ';') -> None:
        self.tokens = tokens
        self.position = position
        self.program = program
        self.endChar = endChar
        self.currentStep = 0
        self.steps = 0

    # Expression Parser
    def generateExpression(self) -> MTNode:
        node = self.parseLogical()
        return self.position, node

        if self.peek() != None:
            MTCompilerMessage.syntaxError(self.program, self.peek(), self.peek().start_pos, 'expression token')
    
    def parseLogical(self) -> MTNode:
        node = self.parseComparison()

        while self.match(MTTokenType.LOGICAL_OPERATOR):
            current = MTNode(self.consume(MTTokenType.LOGICAL_OPERATOR))
            current.left = node
            current.right = self.parseComparison()
            node = current
        
        return node

    def parseComparison(self) -> MTNode:
        node = self.parseTerm()

        if self.match(MTTokenType.CONDITIONAL_OPERATOR):
            current = MTNode(self.consume(MTTokenType.CONDITIONAL_OPERATOR))
            current.left = node
            if current.current.value == '?':
                current.right = self.parseComparison()
                node = current
            else:
                current.right = self.parseTerm()
                node = current

        return node
    
    def parseTerm(self) -> MTNode:
        node = self.parseFactor()

        while self.match(MTTokenType.OPERATOR):
            current = MTNode(self.consume(MTTokenType.OPERATOR))
            current.left = node
            if current.current.value == '++' or current.current.value == '--':
                return current
            else:
                right = self.parseFactor()
                current.right = right
                node = current

        return node
    
    def parseFactor(self) -> MTNode:
        if self.match(MTTokenType.VALUE):
            node = MTNode(self.consume(MTTokenType.VALUE))
            return node
        elif self.match(MTTokenType.IDENTIFIER):
            node = MTNode(self.consume(MTTokenType.IDENTIFIER))
            return node
        elif self.match(MTTokenType.SEPARATOR, expected_value='('):
            self.advance()
            self.position, node = MTExpressionGrammar(self.tokens, self.program, self.position, ')').generateExpression()
            self.advance()
            return node

        if self.peek() != None:
            MTCompilerMessage.syntaxError(self.program, self.peek(), self.peek().start_pos, 'expression token')
    
    # Core Functions
    def match(self, expected_type: MTTokenType, expected_sub_type: MTTokenSubType = MTTokenSubType.NONE, expected_value: str = None) -> bool:
        if self.check(expected_type, expected_sub_type=expected_sub_type, expected_value=expected_value):
            return True
        return False
    
    def consume(self, expected_type: MTTokenType, expected_sub_type: MTTokenSubType = MTTokenSubType.NONE, expected_value: str = None):
        if self.check(expected_type=expected_type, expected_sub_type=expected_sub_type, expected_value=expected_value):
            return self.advance()
        MTCompilerMessage.syntaxError(self.program, self.peek(), self.position, expected='' if expected_value == None else expected_value)
    
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
    
    def expression_len(self) -> int:
        temp_pos = self.position
        while temp_pos < len(self.tokens):
            if self.tokens[temp_pos].value == self.endChar:
                break
            else:
                temp_pos += 1
        return temp_pos - self.position