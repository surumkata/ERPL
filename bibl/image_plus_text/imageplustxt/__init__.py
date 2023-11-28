#!/usr/bin/python3
"""Module to add text to an image
"""

from PIL import Image, ImageDraw, ImageFont
import argparse
import os

current_folder = os.path.dirname(__file__)
__version__ = '0.1.4'

def parse_arguments():
    '''Define and parse arguments using argparse'''
    parser = argparse.ArgumentParser(description='ImagePlusCenterText Script')
    parser.add_argument('--output_image'     ,'-oi'       ,type=str, nargs=1,required=True                                ,help='Output image file')
    parser.add_argument('--input_image'      ,'-ii'       ,type=str, nargs=1,required=True                                ,help='Input image file' )
    parser.add_argument('--text'             ,'-t'        ,type=str, nargs=1,required=True                                ,help='Text'             )
    parser.add_argument('--font_path'        ,'-fp'       ,type=str, nargs=1                                              ,help='Font path'        )
    parser.add_argument('--text_color'       ,'-tc'       ,type=int, nargs=3                                              ,help='Text color (RGB)' )
    parser.add_argument('--min_font_size'    ,'-minfs'    ,type=int, nargs=1                                              ,help='Minimum font size')
    parser.add_argument('--max_font_size'    ,'-maxfs'    ,type=int, nargs=1                                              ,help='Maximum font size')
    parser.add_argument('--width_percentage' ,'-wp'       ,type=float, nargs=1                                            ,help='Width Percentage' )
    parser.add_argument('--height_percentage','-hp'       ,type=float, nargs=1                                            ,help='Height Percentage')
    parser.add_argument('--linebreaker'       ,'-lb'      ,action='store_true'                                            ,help='Linebreaker'     )
    return parser.parse_args()

def calculate_number_of_chars(image_width, font_size, width_percentage, font_path):
    # Especifica a fonte
    font = ImageFont.truetype(font_path, font_size)

    # Calcula a largura real de um caractere
    char_width = font.getsize("a")[0]

    # Calcula o número aproximado de caracteres que cabem na imagem
    chars_numbers = int((image_width * width_percentage) // char_width)

    return chars_numbers

def text_linebreaker(text, max_chars_for_line):
    lines = []
    current_line = ""
    words = text.split()
    for word in words:
        if len(current_line) + len(word) > max_chars_for_line:
            lines.append(current_line.strip())
            current_line = word
        else:
            current_line += " " + word
    lines.append(current_line.strip())
    return lines


def add_text_to_image(image_path, output_path, text, text_color=(255, 255, 255), font_path="arial.ttf", min_font_size=8, linebreaker =False, max_font_size=100, width_percentage=0.8, height_percentage=0.8):
    # Abre a imagem
    original_image = Image.open(image_path)

    # Obtém o tamanho da imagem
    image_width, image_height = original_image.size

    # Cria um objeto para desenhar na imagem
    draw = ImageDraw.Draw(original_image)

    # Inicializa o tamanho da fonte
    font_size = min_font_size

    max_chars_for_line = calculate_number_of_chars(image_width, font_size,width_percentage,font_path)
    if linebreaker:
        lines = text_linebreaker(text,max_chars_for_line)
    else:
        lines = [text]

    # Define o tamanho máximo do texto como 80% da largura da imagem
    max_text_width = int(width_percentage * image_width)

    # Define o tamanho máximo do texto como 80% da altura da imagem
    max_text_height = int(height_percentage * image_height)

    # Ajusta o tamanho da fonte até que o texto caiba dentro da largura máxima
    while lines[0] != "" and draw.textsize(lines[0], ImageFont.truetype(font_path, font_size+1))[0] < max_text_width and font_size < max_font_size:  # Adicionamos uma verificação para evitar loops infinitos
        font_size += 1
    font = ImageFont.truetype(font_path, font_size)

    text_width, text_height = draw.textsize(lines[0], font)
    # Calcula a posição para centralizar o texto
    y = (image_height - len(lines) * text_height) // 2

    # Adiciona o texto à imagem com a cor desejada
    for line in lines:
        text_width, text_height = draw.textsize(line, font)
        # Garante que o texto não ultrapasse os limites da imagem
        if text_width > max_text_width:
            raise ValueError("O seu texto ultrapassa os limites de largura da imagem establecidos.")
        elif y > max_text_height:
            raise ValueError("O seu texto ultrapassa os limites de altura da imagem establecidos.")
        x = (image_width - text_width) // 2

        draw.text((x, y), line, font=font, fill=text_color)
        y += text_height

    # Salva a imagem resultante
    original_image.save(output_path)

def imageplustxt():
    args = parse_arguments()

    image_path = args.input_image[0]
    output_path = args.output_image[0]
    text = args.text[0]
    font_path = args.font_path[0] if args.font_path else f"{current_folder}/fonts/arial.ttf"
    text_color = (args.text_color[0],args.text_color[1],args.text_color[2]) if args.text_color else (255, 255, 255)
    min_font_size = args.min_font_size[0] if args.min_font_size else 8
    max_font_size = args.max_font_size[0] if args.max_font_size else 100
    width_percentage = args.width_percentage[0] if args.width_percentage else 0.8
    height_percentage = args.height_percentage[0] if args.height_percentage else  0.8
    linebreaker = True if args.linebreaker else False

    add_text_to_image(image_path=image_path, output_path=output_path, text=text, text_color=text_color, linebreaker=linebreaker,
                       font_path=font_path, min_font_size=min_font_size, max_font_size=max_font_size, width_percentage= width_percentage, height_percentage=height_percentage)

    print(f'Imagem com texto salva em {output_path}')