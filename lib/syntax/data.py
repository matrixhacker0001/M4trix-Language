from enum import Enum, auto
from lib.lexer.token_class import MTToken

class MTStatementOperation(Enum):
    EXPRESSION = auto()
    ASSIGNMENT = auto()
    DATATYPE = auto()
    COMPUTATION = auto()
    VALUE = auto()
    CONDITIONAL = auto()

class MTNode:
    def __init__(self, current: MTToken) -> None:
        self.current: MTToken = current
        self.left: MTNode = None
        self.right: MTNode = None
        self.statements: list[MTNode] = []
    
    def __repr__(self) -> str:
        return "{" + f'"current": {self.current}, "left":{self.left if self.left != None else "null"}, "right": {self.right if self.right != None else "null"}, "statements": {self.statements}' + "}"