from lib.lexer.token_class import *
from lib.syntax.grammar.statement import *
from lib.message import MTCompilerMessage

class MTSyntaxAnalyzer:
    def __init__(self, tokens: list[MTToken], program: str) -> None:
        self.tokens = tokens
        self.position = 0
        self.program = program
        self.statements: list[MTNode] = []
    
    def analyze(self) -> list[MTNode]:
        while self.position < len(self.tokens):

            if self.match(MTTokenType.KEYWORD, MTTokenSubType.DATA_TYPE_KEYWORDS):
                self.statements.append(self.parseDataType())
            elif self.match(MTTokenType.KEYWORD, expected_value='print'):
                self.statements.append(self.parsePrint())
            elif self.match(MTTokenType.IDENTIFIER):
                self.statements.append(self.parseIdentifier())
            elif self.match(MTTokenType.KEYWORD, MTTokenSubType.CONDITIONAL_KEYWORDS):
                self.statements.append(self.parseConditional())
            elif self.match(MTTokenType.KEYWORD, MTTokenSubType.LOOPS_KEYWORDS):
                self.statements.append(self.parseLoop())
            else:
                MTCompilerMessage.syntaxError(self.program, self.peek(), self.peek().start_pos)
        
        return self.statements
    
    def parseDataType(self) -> MTNode:
        self.position, node = MTStatementGrammar(self.tokens, self.program, self.position).generateStatement()
        self.consume(MTTokenType.SEPARATOR, expected_value=';')
        return node
    
    def parseIdentifier(self) -> MTNode:
        self.position, node = MTStatementGrammar(self.tokens, self.program, self.position).generateStatement()
        self.consume(MTTokenType.SEPARATOR, expected_value=';')
        return node
    
    def parseConditional(self) -> MTNode:
        self.position, node = MTStatementGrammar(self.tokens, self.program, self.position).generateStatement()
        return node
    
    def parseLoop(self) -> MTNode:
        self.position, node = MTStatementGrammar(self.tokens, self.program, self.position).generateStatement()
        return node
    
    def parsePrint(self) -> MTNode:
        self.position, node = MTStatementGrammar(self.tokens, self.program, self.position).generateStatement()
        self.consume(MTTokenType.SEPARATOR, expected_value=';')
        return node
    
    # Core Functions
    def match(self, expected_type: MTTokenType, expected_sub_type: MTTokenSubType = MTTokenSubType.NONE, expected_value: str = None) -> bool:
        if self.check(expected_type, expected_sub_type=expected_sub_type, expected_value=expected_value):
            return True
        return False
    
    def consume(self, expected_type: MTTokenType, expected_sub_type: MTTokenSubType = MTTokenSubType.NONE, expected_value: str = None):
        if self.check(expected_type=expected_type, expected_sub_type=expected_sub_type, expected_value=expected_value):
            return self.advance()
        
        if self.peek() != None:
            MTCompilerMessage.syntaxError(self.program, self.peek(), self.peek().start_pos, expected='' if expected_value == None else expected_value)
        else:
            MTCompilerMessage.syntaxError(self.program, self.previous(), self.previous().start_pos, expected='' if expected_value == None else expected_value)
    
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