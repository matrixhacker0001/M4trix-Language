from lib.lexer.token_class import *

class MTCompilerMessage:
    def __init__(self) -> None:
        pass

    @staticmethod
    def error(msg: str):
        print(f'\n\033[31m{msg}\033[0m\n')
        exit(1)
    
    @staticmethod
    def warning(msg: str):
        print(f'\n\033[33mWarning: {msg}\033[0m\n')
    
    @staticmethod
    def success(msg: str):
        print(f'\n\033[32m{msg}\033[0m\n')
    
    @staticmethod
    def lexerError(file: str, program: str, char: str, position: int):
        line_number = MTCompilerMessage.get_line_number(program, position)
        column_number = MTCompilerMessage.get_column_number(program, position)

        msg = f'{file}:{line_number}:{column_number}: Error: Unexpected character found: \'{char}\'.\n'
        msg += f'    {MTCompilerMessage.print_string_at_line(program, line_number)}\n'
        msg += f'    {''.join(str(' ') for x in range(1, column_number))}^'
        MTCompilerMessage.error(msg)
    
    @staticmethod
    def get_line_number(text, position):
        # Count the number of newline characters up to the position
        line_number = text.count('\n', 0, position) + 1
        return line_number
    
    @staticmethod
    def get_column_number(text, position):
        line_start = text.rfind('\n', 0, position)
        column_number = position - line_start
        return column_number
    
    @staticmethod
    def print_string_at_line(text, line_number):
        lines = text.split('\n')
        # Ensure the line_number is within the range of existing lines or the next line to append
        if line_number < 1 or line_number > len(lines) + 1:
            raise IndexError("Line number out of range")
        return lines[line_number - 1]
    
    @staticmethod
    def syntaxError(program: str, token: MTToken, position: int, expected: str = ''):
        line_number = MTCompilerMessage.get_line_number(program, position)
        column_number = MTCompilerMessage.get_column_number(program, position)

        msg = f'{token.file}:{line_number}:{column_number}: Error: Unexpected token found \'{token.value}\'.\n'
        msg += f'    {MTCompilerMessage.print_string_at_line(program, line_number)}\n'
        msg += f'    {''.join(str(' ') for x in range(1, column_number))}^'
        msg += f'{'\nExpected: ' + expected if expected != '' else ''}'
        MTCompilerMessage.error(msg)
    
    @staticmethod
    def semanticError(program: str, token: MTToken, position: int, error: str, expected: str = ''):
        line_number = MTCompilerMessage.get_line_number(program, position)
        column_number = MTCompilerMessage.get_column_number(program, position)

        msg = f'{token.file}:{line_number}:{column_number}: Error: {error}.\n'
        msg += f'    {MTCompilerMessage.print_string_at_line(program, line_number)}\n'
        msg += f'    {''.join(str(' ') for x in range(1, column_number))}^'
        msg += f'{'\nExpected: ' + expected if expected != '' else ''}'
        MTCompilerMessage.error(msg)