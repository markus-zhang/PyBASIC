```python
"""
    Tokenizer for Tiny BASIC

"""

from enum import Enum

KEYWORDS = ['PRINT', 'END', 'LET', 'GOTO', 'GOSUB', 'RETURN', 'FOR', 'NEXT', 'STOP', 'INPUT', 'IF', 'REM']

class TokenType(Enum):
    # Keywords
    TOKEN_PRINT = 0
    TOKEN_END = 1
    TOKEN_LET = 2
    TOKEN_GOTO = 3
    TOKEN_GOSUB = 4
    TOKEN_RETURN = 5
    TOKEN_FOR = 6
    TOKEN_NEXT = 7
    TOKEN_STOP = 8
    TOKEN_INPUT = 9
    TOKEN_IF = 10
    TOKEN_REM = 11

    # Literals
    TOKEN_IDENTIFIER = 100
    TOKEN_STRING = 101
    TOKEN_NUMBER = 102

    # Single-char
    TOKEN_LEFT_PAREN = 200
    TOKEN_RIGHT_PAREN = 201
    TOKEN_COMMA = 202
    TOKEN_DOT = 203
    TOKEN_MINUS = 204
    TOKEN_PLUS = 205
    TOKEN_SLASH = 206
    TOKEN_ASTERISK = 207

    # Line-number
    TOKEN_LINE_NUMBER = 300
    

class Token:
    def __init__(self, type:TokenType, lexeme:str, literal:object, line:int, offset:int):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
        self.offset = offset

    def debugPrint(self, sourceByLine:list[str]):
        """
            Print the line the token is in
            Print a second line with ^ pointing to the token in the previous line
            Example:
            10 PRINT "Hello, World!"
            ---------^

            sourceByLine is supposed to be broken down into a list
        """
        print(sourceByLine[self.line])

        for i in range(self.offset):
            print('-', end='')
        
        print('^')


class Scanner:
    def __init__(self, source:str):
        self.sourceByLine = source.split('\n')
        # Remove leading and trailing spaces
        for line in self.sourceByLine:
            line = line.strip()
        self.tokens = []
        self.offsetBegin = 0
        self.offsetEnd = 0
        self.scanTokens()

    def debugPrint(self):
        for index, item in enumerate(self.sourceByLine):
            print(f"Line {index}: {item}")

    def exceptionPrint(self, currentLine:int):
        """
            Print the line,
            print - until offsetBegin, and then - until offsetEnd
        """
        print(self.sourceByLine[currentLine])
        print('-' * self.offsetBegin, end='')
        print('^', end='')
        print('-' * (self.offsetEnd - self.offsetBegin), end='')
        if (self.offsetEnd > self.offsetBegin):
            print('^') 

    def scanTokens(self):
        """
            For each token we also need to record line and offset,
            also some tokens are not separated by spaces (e.g. 1 + 3 can also be 1+3),
            so it's just easier to maintain two offset pointers, 
            one pointing at the beginning, one moving towards the end.
            Then we slice the string to make the token lexeme.
        """
        for index, item in enumerate(self.sourceByLine):
            tokenLine = index
            maxOffset = len(item) - 1  # offsetEnd <= maxOffset
            # Reset offset pointers
            self.offsetBegin = 0
            self.offsetEnd = 0

            singleCharOp = ['(', ')', ',', '.', '-', '+', '/', '*']

            while self.offsetEnd <= maxOffset:
                currentChar = item[self.offsetBegin]

                # Single Char Op
                """
                    # Single-char
                    TOKEN_LEFT_PAREN = 200
                    TOKEN_RIGHT_PAREN = 201
                    TOKEN_COMMA = 202
                    TOKEN_DOT = 203
                    TOKEN_MINUS = 204
                    TOKEN_PLUS = 205
                    TOKEN_SLASH = 206
                    TOKEN_ASTERISK = 207
                """
                if currentChar in singleCharOp:
                    self._addToken(TokenType.TOKEN_LEFT_PAREN + singleCharOp.index(currentChar), tokenLine, item)
                
                # strings
                elif currentChar == '"':
                    # String should start from offsetEnd's initial position
                    # offsetEnd should point to the closing double quote

                    # TODO: This is wrong, what if the first character of a line is '"'? offsetEnd would be 0 too
                    # TODO: Also, probably need to revise the whole scheme as well, I want to directly compile to machine code
                    # TODO: I also need to check whether first token is TOKEN_LINE_NUMBER (right now enforced while Tiny BASIC allows no line number -> immediately execute)
                    while (item[self.offsetEnd] != '='):
                        self.offsetEnd += 1
                        if self.offsetEnd > maxOffset:
                            # Exception should never terminate the scanner,
                            # it ignores the item, moves both offset pointers and continue scanning
                            self.exceptionPrint(tokenLine)
                            break
                    # Now offsetEnd points to the closing double quote (TODO: maybe use do...while...)
                    self._addToken(TokenType.TOKEN_STRING, tokenLine, item)
                
                # keywords and identifiers, first char must be a~z
                elif currentChar.isalpha():
                    # offsetEnd should point to the last char of the identifier/keyword
                    # the rest of the characters can be alphanumeric
                    while item(self.offsetEnd).isalnum():
                        self.offsetEnd += 1
                        if self.offsetEnd == maxOffset:
                            break

                    # Check whether it is a KEYWORD or an IDENTIFIER
                    lexeme = item[self.offsetBegin : self.offsetEnd + 1].upper()
                    if lexeme in KEYWORDS:
                        self._addToken(TokenType(KEYWORDS.index(lexeme)), tokenLine, item)
                    else:
                        self._addToken(TokenType.TOKEN_IDENTIFIER, tokenLine, item)

                # numbers, we don't support scientific numerical such as 1E-8 yet, so just integers and floats
                elif currentChar.isdigit():
                    
 
                # We always move offsetEnd forward before conclusion
                # So we need to make sure, EVERY scanner branch needs to put offsetEnd at the right place
                # e.g. for strings, offsetEnd should point to the closing double quote, not the next char
                self.offsetEnd += 1
                self.offsetBegin = self.offsetEnd



    def _addToken(self, type:TokenType, tokenLine:int, line:str):
        if type >= TokenType.TOKEN_LEFT_PAREN and type <= TokenType.TOKEN_ASTERISK:
            self.tokens.append(
                Token(
                    type, 
                    line[self.offsetBegin], 
                    line[self.offsetBegin], 
                    tokenLine, 
                    self.offsetBegin
                )
            )
        elif type == TokenType.TOKEN_STRING:
            # offsetEnd now points to the closing quote
            # we DO NOT want to keep the char (opening double quote) at offsetEnd
            self.tokens.append(
                Token(
                    type, 
                    line[self.offsetBegin + 1 : self.offsetEnd], 
                    line[self.offsetBegin + 1 : self.offsetEnd]),
                    tokenLine,
                    self.offsetBegin
            )
        elif (type >= TokenType.TOKEN_PRINT and type <= TokenType.TOKEN_REM) or type == TokenType.TOKEN_IDENTIFIER:
            # offsetEnd now points to the last char
            # we want to keep the char at offsetBegin
            self.tokens.append(
                Token(
                    type, 
                    line[self.offsetBegin : self.offsetEnd + 1], 
                    line[self.offsetBegin : self.offsetEnd + 1]),
                    tokenLine,
                    self.offsetBegin
            )
```