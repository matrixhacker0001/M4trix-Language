from enum import Enum, auto
import json

class MTTokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    VALUE = auto()
    OPERATOR = auto()
    CONDITIONAL_OPERATOR = auto()
    LOGICAL_OPERATOR = auto()
    SEPARATOR = auto()
    STATEMENT_END = auto()
    DOT = auto()
    
    LOOP_LOGIC = auto()

class MTTokenSubType(Enum):
    NONE = auto()

    # Keywords
    DATA_TYPE_KEYWORDS = auto()
    CONDITIONAL_KEYWORDS = auto()
    LOOPS_KEYWORDS = auto()
    OTHER_KEYWORDS = auto()

    # Values
    NUMBER_VALUE = auto()
    DOUBLE_VALUE = auto()
    STRING_VALUE = auto()
    BOOLEAN_VALUE = auto()

class MTToken:
    def __init__(self, type: MTTokenType, value: str, start_pos: int, end_pos: int, sub_type: MTTokenSubType = MTTokenSubType.NONE, line: int = 0, column: int = 0, file: str = ''):
        self.type = type
        self.sub_type = sub_type
        self.value = value
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.line = line
        self.column = column
        self.file = file

    def __repr__(self) -> str:
        return "{" + f'"etype": "MTToken", "type": "{self.type}", "sub_type": "{self.sub_type}", "value": "{self.value}", "start_pos": {self.start_pos}, "end_pos": {self.end_pos}, "line": {self.line}, "column": {self.column}, "file": {json.dumps(self.file)}' + "}"