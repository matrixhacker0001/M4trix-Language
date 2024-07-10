class MTDict:
    def __init__(self) -> None:
        pass

    # keywords for the code
    keywords = {
        # Data Types
        # 'var',
        'int',
        'double',
        'str',
        'bool',

        # Conditional Keywords
        'if',
        'elif',
        'else',
        'switch',
        'case',
        'default',

        # loops
        'for',
        'while',
        'do',

        # other
        'break',
        'continue',
        'return',
        'print',
        'pass'
    }
    dataTypeKeywords = {
        'int',
        'double',
        'str',
        'bool',
    }
    conditionalKeywords = {
        'if',
        'elif',
        'else',
        'switch',
        'case',
        'default',
    }
    loopKeywords = {
        'for',
        'while',
        'do',
    }
    otherKeywords = {
        'break',
        'continue',
        'return',
        'null',
        'pass'
    }

    # operators for the code
    operators = {'+', '-', '*', '/', '=', '==', '?', ':', '<', '>', '<=', '>=', '&', '|'}
    computationalOperators = {'+', '-', '*', '/'}
    conditionalOperators = {'==', '?', ':', '<', '>', '<=', '>='}
    logicalOperators = {'&&', '||'}

    # separators for the code
    separators = {';', ',', '(', ')', '{', '}'}

    # booleans variables
    booleans = {'false', 'true', '0', '1'}