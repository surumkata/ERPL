import os
from .parser.parser import parse
from .engine.game import init_game, play_game
from .engineP5.p5_export import export_for_p5  # Agora estamos importando da pasta engineP5
from .parser.obj_parser import parse_new_obj
import json

import argparse
import subprocess
import shutil

__version__ = "0.1.11"

current_folder = os.path.dirname(__file__)

def game_parse_arguments():
    '''Define and parse arguments using argparse'''
    parser = argparse.ArgumentParser(description='ERPL Engine')
    parser.add_argument('--input', '-i', type=str, nargs=1, help='Input file')
    parser.add_argument('--engine', '-e', choices=["pygame", "p5"], default="pygame", help="Escolha a engine do jogo: pygame ou p5.js")
    parser.add_argument('--delete-tmp', '-dtmp', action='store_true', help='Remove arquivos temporários da pasta /erpl/engineP5/tmp/')
    return parser.parse_args()

def erpl_parse_arguments():
    '''Define and parse arguments using argparse'''
    parser = argparse.ArgumentParser(description='ERPL')
    parser.add_argument('--output', '-o', type=str, nargs=1, help='Output file')
    parser.add_argument('--input', '-i', type=str, nargs=1, help='Input file')
    parser.add_argument('--args', '-args', nargs='+', help='Args')
    parser.add_argument('--engine', '-e', choices=["pygame", "p5"], default="pygame", help="Escolha a engine do jogo: pygame ou p5.js")
    parser.add_argument('--delete-tmp', '-dtmp', action='store_true', help='Remove arquivos temporários da pasta /erpl/engineP5/tmp/')
    return parser.parse_args()

def parser_parse_arguments():
    '''Define and parse arguments using argparse'''
    parser = argparse.ArgumentParser(description='ERPL Compiler')
    parser.add_argument('--output','-o'            ,type=str, nargs=1,required=False                                , help='Output file')
    parser.add_argument('--input','-i'             ,type=str, nargs=1,required=True                                 , help='Input file')
    parser.add_argument('--args','-args'           ,nargs='+'                                                       , help='Args')
    return parser.parse_args()
    

def erbib_parse_arguments():
    '''Define and parse arguments for managing the library of objects'''
    parser = argparse.ArgumentParser(description='ERPL Biblioteca de Objetos')
    parser.add_argument('--list', '-l', action='store_true', help='Listar todos os objetos')
    parser.add_argument('--add', '-a', type=str, nargs=2, metavar=('ID', 'FILE'), help='Adicionar um novo objeto com ID e arquivo de obj')
    parser.add_argument('--remove', '-r', type=str, nargs=1, metavar=('ID'), help='Remover um objeto existente')
    parser.add_argument('--inspect', '-i', type=str, nargs=1, metavar=('ID'), help='Inspecionar um objeto existente')
    return parser.parse_args()


def clear_tmp_directory():
    """Remove todos os arquivos na pasta /erpl/engineP5/tmp/."""
    tmp_dir = os.path.join(os.path.dirname(__file__), 'engineP5', 'tmp')
    if os.path.exists(tmp_dir):
        for filename in os.listdir(tmp_dir):
            file_path = os.path.join(tmp_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print("Arquivos temporários removidos de /erpl/engineP5/tmp/.")

def erpl():
    args = erpl_parse_arguments()
    
    # Verificar se a flag -dtmp foi passada
    if args.delete_tmp:
        clear_tmp_directory()
        if not args.input:
            return

    # Verificar se o arquivo de input foi passado
    if not args.input:
        print("Erro: Um arquivo de input é necessário para rodar o comando.")
        return
    
    # Gerar o arquivo JSON temporário
    if args.output:
        print("ERROR!")
    args.output = ['tmp.json']  # TODO: Gerar nome de arquivo baseado na data e hora
    parse(args)
    
    # Escolher a engine
    args.input = ['tmp.json']
    if args.engine == "pygame":
        screen, room, inventory, state = init_game(args)
        os.remove('tmp.json')
        # Joga usando o Pygame
        play_game(screen, room, inventory, state)
    elif args.engine == "p5":
        # Exportar os dados do jogo para o formato p5.js
        export_for_p5(args.input[0])
        os.remove('tmp.json')

        # Opcional: rodar o jogo em um servidor local para testar
        print("Rodando jogo com engine p5.js. Iniciando em http://localhost:3000")
        subprocess.run(["python", "-m", "http.server", "3000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def erparse():
    args = parser_parse_arguments()
    parse(args)
    

def erengine():
    args = game_parse_arguments()

    # Verificar se a flag -dtmp foi passada
    if args.delete_tmp:
        clear_tmp_directory()
        if not args.input:
            return

    # Verificar se o arquivo de input foi passado
    if not args.input:
        print("Erro: Um arquivo de input é necessário para rodar o comando.")
        return

    if args.engine == "pygame":
        screen, room, inventory, state = init_game(args)
        play_game(screen, room, inventory, state)
    elif args.engine == "p5":
        export_for_p5(args.input[0])
        print("Rodando jogo com engine p5.js. Iniciando em http://localhost:3000")
        subprocess.run(["python", "-m", "http.server", "3000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


import os
import shutil

# Função para copiar arquivos e atualizar caminhos
def copy_and_update_paths(data, dest_path):
    copied_files = {}  # Dicionário para mapear original_path para new_filename
    
    for section in ['views', 'sounds']:
        for item in data.get(section, []):
            if 'sources' not in item:
                continue
            for source in item['sources']:
                if source[0] == "PATH":
                    original_path = source[1]
                    
                    if not os.path.exists(original_path):
                        print(f"Aviso: Arquivo '{original_path}' não encontrado para cópia.")
                        continue
                    
                    # Verificar se já copiamos esse arquivo anteriormente
                    if original_path in copied_files:
                        # Reutilizar o nome do arquivo existente
                        source[1] = copied_files[original_path]
                    else:
                        # Criar um novo nome de arquivo único, se necessário
                        base_filename = os.path.basename(original_path)
                        new_filename = base_filename
                        new_path = os.path.join(dest_path, new_filename)
                        
                        # Adicionar um sufixo se o nome do arquivo já existe no destino
                        counter = 1
                        while os.path.exists(new_path):
                            name, ext = os.path.splitext(base_filename)
                            new_filename = f"{name}_{counter}{ext}"
                            new_path = os.path.join(dest_path, new_filename)
                            counter += 1
                        
                        # Copiar o arquivo para o novo diretório e atualizar o dicionário
                        shutil.copy(original_path, new_path)
                        copied_files[original_path] = new_filename  # Mapeia o caminho original para o novo nome
                        source[1] = new_filename


def erbib():
    args = erbib_parse_arguments()
    dest_dir = 'erpl/assets/objects'

    # Listar cenários e objetos
    if args.list:
        print("\nObjetos disponíveis:")
        for obj in os.listdir(dest_dir):
            print(f"- {obj}")

    elif args.add:
        id_, file_path = args.add

        if not os.path.isfile(file_path):
            print("Erro: O arquivo especificado não existe.")
            return
        
        try:
            obj = parse_new_obj(file_path, id_, current_folder)  # Transforma o arquivo em um dicionário
        except Exception as e:
            print(e)
            print("Object not valid")
            return

        # Caminho completo do diretório de destino
        dest_path = os.path.join(dest_dir, id_)
        
        # Verificar se o ID já existe
        if os.path.exists(dest_path):
            print(f"Erro: Objeto com o ID '{id_}' já existe.")
            return
        
        # Criar o diretório com o ID especificado
        os.makedirs(dest_path, exist_ok=True)
        
        # Copiar os arquivos referenciados e atualizar os caminhos
        copy_and_update_paths(obj,dest_path)

        # Salvar o dicionário atualizado como um JSON na nova pasta
        json_path = os.path.join(dest_path, f"{id_}.json")
        with open(json_path, 'w') as json_file:
            json.dump(obj, json_file, indent=4)
        
        print(f"Objeto '{id_}' adicionado com sucesso à biblioteca.")

    # Remover cenário ou objeto
    elif args.remove:
        id_ = args.remove[0]
        remove_path = os.path.join(dest_dir, id_)

        if os.path.exists(remove_path):
            shutil.rmtree(remove_path)
            print(f"Objeto '{id_}' removido com sucesso de {remove_path}.")
        else:
            print(f"Objeto '{id_}' não encontrado.")

    elif args.inspect:
        id_ = args.inspect[0]
        path = os.path.join(dest_dir, id_)
        if os.path.exists(path):
            json_path = os.path.join(path,f'{id_}.json')
            file = open(json_path)
            code = file.read()
            print(code)
        else:
            print(f"Objeto '{id_}' não encontrado.")

    else:
        print("Comando inválido. Use '--list' para listar, '--add ID EROBJ_FILE' para adicionar ou '--remove ID' para remover.")


