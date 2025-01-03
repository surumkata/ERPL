# ERPL

Warning: Still development

ERPL (Escape Room Programming Language) is a programming language to facilitate the creation of virtual escape room games. The program is composed of a parser and an engine (both can be used separately). The parser will receive an .erpl file (described below) that will have the escape room information, it will analyze it and then the engine with this information will generate the escape room game, with the help of the pygame module.

## Parser

        erparse <.erpl file>

### Options

     -h, --help                                      show this help message and exit
     -o OUTPUT , --output OUTPUT                     output (json) file (default is stdout)
     -i INPUT , --input  INPUT                       input file (.erpl file)
     -args ARGS [ARGS ...], --args ARGS [ARGS ...]   arguments to be replaced in the erpl file

## Engine

     erengine <json file>   

### Options

    -h, --help                                      show this help message and exit
    -i INPUT , --input  INPUT                       input file (json file)
    -e ENGINE, --engine ENGINE                      Escolha a engine do jogo: pygame ou p5
