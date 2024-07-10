import sys
import os
import json

from lib.lexer.lexer import MTLexerAnalyzer
from lib.syntax.syntax import MTSyntaxAnalyzer
from lib.semantic.semantic import MTSemanticAnalysis
from lib.interpreter.interpreter import MTInterpreter
from lib.message import MTCompilerMessage

def read_file(file_path):
    try:
        clear__build_files('./bin/tokens.json')
        clear__build_files('./bin/tokens.json_error')
        clear__build_files('./bin/asts.json')
        clear__build_files('./bin/asts.json_error')
        clear__build_files('./bin/interpreter.json')
        clear__build_files('./bin/interpreter.json_error')
        clear__build_files('./bin/semantic.json')
        clear__build_files('./bin/semantic.json_error')

        with open(file_path, 'r') as file:
            content = file.read()

            # Generating Tokens from the script
            lexer = MTLexerAnalyzer(content, file_path)
            tokens = lexer.tokenize()
            generate_build_files('./bin/tokens.json', str(tokens))

            # Parsing Tokens for Syntax Analysis and AST Tree
            syntax = MTSyntaxAnalyzer(tokens, content)
            asts = syntax.analyze()
            generate_build_files('./bin/asts.json', str(asts))

            # Parsing Nodes for Semantic Analysis and Check Proper Meaning
            semantic = MTSemanticAnalysis(asts, content, {})
            data = semantic.analyze()
            generate_build_files('./bin/semantic.json', str(json.dumps(data)))

            # Interpret Nodes
            interpreter = MTInterpreter(asts, content)
            data = interpreter.interpret()
            generate_build_files('./bin/interpreter.json', str(json.dumps(data)))

            file.close()

            # Prints for success message on compiler complete
            # MTCompilerMessage.success("Compiler Completed Successfully.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except IOError:
        print(f"Error reading from file '{file_path}'.")

def generate_build_files(file_path, content: str):
    try:
        with open(file_path, 'w') as file:
            json.dump(json.loads(content), file, indent=4, sort_keys=False)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except IOError:
        print(f"Error reading from file '{file_path}'.")
    except:
        with open(f'{file_path}_error', 'w') as file:
            file.write(content)
            file.close()

def clear__build_files(file_path):
    if (os.path.exists(file_path)):
        os.remove(file_path)

if __name__ == "__main__":
    # Check if a file path is provided as an argument
    if len(sys.argv) != 2:
        print(f"Usage: {os.path.basename(__file__)} <file_path>")
        sys.exit(1)
    
    # Get the file path from the command-line argument
    file_path = sys.argv[1]
    
    # Call the function to read and display the file contents
    read_file(file_path)