'''
Created on 2013-05-21

@author: kjnether

  This is an attempt to write a parser for the .dnet file format using the ply
  module.
  
  5-21-2013 - Played around with this 
'''


import ply.lex as lex

tokens = ['TYPE',
          'NAME', 
          'NUMBER',
          'STRING',
          'LPAREN',
          'RPAREN',
          'LBRACKET',
          'RBRACKET',
          'COMMENT',
          'COMMA',
          'EQUALS', 
          'STMTEND',
          'LINECONTINUATION']

t_LPAREN  = r'\{'
t_RPAREN  = r'\}'
t_LBRACKET = r'\('
t_RBRACKET = r'\)'
t_TYPE = r'[a-zA-Z]+'
t_NAME = r'[a-zA-Z]+'
t_ignore  = ' \t'
t_COMMENT = '//'
t_NUMBER = '[0-9]+'
t_EQUALS = '='
t_COMMA = ','
t_STMTEND = '\;'
t_STRING = r'".*"'
t_LINECONTINUATION = r'\\'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    


def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)


literals = "="


inputFile = r'W:\ilmb\vic\geobc\bier\p14\p14_0053_BBN_CumEffects\wrk\netica\Car_Buyer_Subset.txt'
fh = open(inputFile, 'r')
fileContents = fh.read()
fh.close()
print fileContents
print '------------------------\n\n\n\n'
lex.lex()
lex.input(fileContents) # @UndefinedVariable
while True:
    tok = lex.token() # @UndefinedVariable
    # type, value, line, lexpos
    print tok
    if not tok:
        break





