from lib.lexer.token_class import *
from lib.dict import *
from lib.message import *

class MTLexerAnalyzer:
    def __init__(self, program, file):
        self.program = program
        self.file = file
        self.position = 0
        self.tokens = []
        pass

    def tokenize(self):
        while self.position < len(self.program):
            char: str = self.program[self.position]
            
            # check if current char is space and continue to read another characters
            if char.isspace():
                self.position += 1
                continue

            # check if identifier or keyword
            elif char.isalpha():
                self.tokenizeKeywordIdentifier()

            # check for comments
            elif char == '#' or (char == '/' and len(self.program) > self.position and self.program[self.position + 1] == '/'):
                self.tokenizeComment()
            
            # check if number
            elif char.isdigit() or (char == '-' and self.is_next_digit()):
                self.tokenizeDigit()
            
            # check if string
            elif char == "'" or char == '"':
                self.position += 1
                self.tokenizeString(char)
            
            # check if statement end
            elif char == ';':
                self.tokenizeStatementEnd()
            
            # check if separator
            elif char in MTDict.separators:
                self.tokenizeSeparator()
            
            # check if dot
            elif char == '.':
                self.tokenizeDot()
            
            # check if operator
            elif char in MTDict.operators:
                self.tokenizeOperator()

            # throws error when not in the configured settings
            else:
                MTCompilerMessage.lexerError(self.file, self.program, char, self.position)

        return self.tokens
    
    def tokenizeComment(self) -> bool:
        if (self.program[self.position] == '/' and len(self.program) - 1 > self.position and self.program[self.position + 1] == '/') or (self.program[self.position] == '#'):
            self.position += 2
            while len(self.program) > self.position and self.program[self.position] != '\n':
                self.position += 1
            return True
        return False
    
    def tokenizeKeywordIdentifier(self):
        start_pos = self.position
        while self.position < len(self.program) and self.program[self.position].isalnum():
            self.position += 1
        
        value = self.program[start_pos:self.position]
        sub_type = MTTokenSubType.NONE
        if value in MTDict.booleans:
            value_type = MTTokenType.VALUE
            sub_type = MTTokenSubType.BOOLEAN_VALUE
        elif value in MTDict.keywords:
            value_type = MTTokenType.KEYWORD
            if value in MTDict.dataTypeKeywords:
                sub_type = MTTokenSubType.DATA_TYPE_KEYWORDS
            elif value in MTDict.conditionalKeywords:
                sub_type = MTTokenSubType.CONDITIONAL_KEYWORDS
            elif value in MTDict.loopKeywords:
                sub_type = MTTokenSubType.LOOPS_KEYWORDS
            elif value in MTDict.otherKeywords:
                sub_type = MTTokenSubType.OTHER_KEYWORDS
        else:
            value_type = MTTokenType.IDENTIFIER

        self.tokens.append(MTToken(value_type, value, start_pos, self.position, sub_type, file = self.file, line = self.program.count('\n', 0, self.position) + 1, column = start_pos - self.program.rfind('\n', 0, self.position)))

    def tokenizeOperator(self):
        start_pos = self.position
        while self.position < len(self.program) and self.program[self.position] in MTDict.operators:
            self.position += 1
        
        value = self.program[start_pos:self.position]
        if value in MTDict.conditionalOperators:
            etype = MTTokenType.CONDITIONAL_OPERATOR
        elif value in MTDict.logicalOperators:
            etype = MTTokenType.LOGICAL_OPERATOR
        elif value in MTDict.computationalOperators:
            etype = MTTokenType.OPERATOR
        else:
            etype = MTTokenType.OPERATOR
        self.tokens.append(MTToken(etype, value, start_pos, self.position, file = self.file, line = self.program.count('\n', 0, self.position) + 1, column = start_pos - self.program.rfind('\n', 0, self.position)))

    def tokenizeDigit(self):
        start_pos = self.position
        isDotUsed = False
        if self.program[self.position] == '-':
            self.position += 1  # Skip the minus sign
        while self.position < len(self.program) and (self.program[self.position].isdigit() or (self.program[self.position] == '.' and not isDotUsed)):
            if not isDotUsed and self.program[self.position] == '.':
                isDotUsed = True
            self.position += 1
        
        value = self.program[start_pos:self.position]
        sub_type = MTTokenSubType.NUMBER_VALUE
        if isDotUsed:
            sub_type = MTTokenSubType.DOUBLE_VALUE
        self.tokens.append(MTToken(MTTokenType.VALUE, value, start_pos, self.position, sub_type = sub_type, file = self.file, line = self.program.count('\n', 0, self.position) + 1, column = start_pos - self.program.rfind('\n', 0, self.position)))
    
    def tokenizeString(self, start_str):
        start_pos = self.position

        while self.position < len(self.program) and self.program[self.position] != '\n':
            if self.program[self.position] == start_str and self.position != 0 and self.program[self.position - 1] != '\\':
                break
            self.position += 1
        
        value = self.program[start_pos:self.position]
        self.position += 1
        self.tokens.append(MTToken(MTTokenType.VALUE, value, start_pos, self.position, sub_type = MTTokenSubType.STRING_VALUE, file = self.file, line = self.program.count('\n', 0, self.position) + 1, column = start_pos - self.program.rfind('\n', 0, self.position)))

    def tokenizeSeparator(self):
        start_pos = self.position
        self.position += 1
        # while self.position < len(self.program) and self.program[self.position] in MTDict.separators and self.program[self.position] != ';':
        #     self.position += 1
        
        value = self.program[start_pos:self.position]
        self.tokens.append(MTToken(MTTokenType.SEPARATOR, value, start_pos, self.position, file = self.file, line = self.program.count('\n', 0, self.position) + 1, column = start_pos - self.program.rfind('\n', 0, self.position)))
    
    def tokenizeStatementEnd(self):
        start_pos = self.position
        while self.position < len(self.program) and self.program[self.position] == ';':
            self.position += 1
        
        value = self.program[start_pos:self.position]
        self.tokens.append(MTToken(MTTokenType.SEPARATOR, value, start_pos, self.position, file = self.file, line = self.program.count('\n', 0, self.position) + 1, column = start_pos - self.program.rfind('\n', 0, self.position)))
    
    def tokenizeDot(self):
        start_pos = self.position
        while self.position < len(self.program) and self.program[self.position] == '.':
            self.position += 1
        
        value = self.program[start_pos:self.position]
        self.tokens.append(MTToken(MTTokenType.DOT, value, start_pos, self.position, file = self.file, line = self.program.count('\n', 0, self.position) + 1, column = start_pos - self.program.rfind('\n', 0, self.position)))
    
    def is_next_digit(self):
        return (self.position + 1 < len(self.program)) and self.program[self.position + 1].isdigit()