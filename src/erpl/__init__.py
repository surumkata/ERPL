"""Módulo principal para o pacote erpl.

Este módulo contém a lógica principal da aplicação erpl.
"""

import argparse
from .parser.parser import parse, parser_parse_arguments
from .engine.game import init_game, game_parse_arguments
from .engine.pe import init_pe, pe_parse_arguments

__version__ = "0.1"

def erpl():
    args = parser_parse_arguments()
    if args.output:
        print("ERROR!")
    parse(args)
    init_game()

def erparse():
    args = parser_parse_arguments()
    parse(args)

def erengine():
    args = game_parse_arguments()
    init_game(args)

def erpe():
    args = pe_parse_arguments()
    init_pe(args)