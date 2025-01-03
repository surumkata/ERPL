import shutil
import os
import json

def export_for_p5(json_file):
    """Move o arquivo JSON gerado para o diretório da engine P5.js e ajusta os caminhos das imagens."""
    output_dir = os.path.join(os.path.dirname(__file__), 'tmp')
    dest_file = os.path.join(output_dir, 'game_model.json')
    
    # Criar o diretório tmp caso não exista
    os.makedirs(output_dir, exist_ok=True)
    
    # Carregar o arquivo JSON
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Função para atualizar caminhos e mover arquivos
    def update_paths_and_move_files(data):
        # Verificar e atualizar caminhos nas views
        for scenario in data.get('scenarios', []):
            for view in scenario.get('views', []):
                for source in view.get('sources', []):
                    if source[0] == "PATH":
                        original_path = source[1]
                        new_filename = os.path.basename(original_path)
                        new_path = os.path.join(output_dir, new_filename)
                        
                        # Mover o arquivo para o novo diretório
                        shutil.copy(original_path, new_path)
                        
                        # Atualizar o caminho no JSON para o formato desejado
                        source[1] = f'/erpl/engineP5/tmp/{new_filename}'

            for obj in scenario.get('objects', []):
                for view in obj.get('views', []):
                    for source in view.get('sources', []):
                        if source[0] == "PATH":
                            original_path = source[1]
                            new_filename = os.path.basename(original_path)
                            new_path = os.path.join(output_dir, new_filename)
                            
                            # Mover o arquivo para o novo diretório
                            shutil.copy(original_path, new_path)
                            
                            # Atualizar o caminho no JSON para o formato desejado
                            source[1] = f'/erpl/engineP5/tmp/{new_filename}'

        # Verificar e atualizar caminhos nas transições
        for transition in data.get('transitions', []):
            for source in transition.get('view', {}).get('sources', []):
                if source[0] == "PATH":
                    original_path = source[1]
                    new_filename = os.path.basename(original_path)
                    new_path = os.path.join(output_dir, new_filename)
                    
                    # Mover o arquivo para o novo diretório
                    shutil.copy(original_path, new_path)
                    
                    # Atualizar o caminho no JSON para o formato desejado
                    source[1] = f'/erpl/engineP5/tmp/{new_filename}'

            # Atualizar o caminho da música
            music_src = transition.get('music', {}).get('src')
            if music_src and os.path.exists(music_src):
                new_music_filename = os.path.basename(music_src)
                new_music_path = os.path.join(output_dir, new_music_filename)
                shutil.copy(music_src, new_music_path)
                transition['music']['src'] = f'/erpl/engineP5/tmp/{new_music_filename}'

    # Atualizar os caminhos e mover os arquivos
    update_paths_and_move_files(data)

    # Salvar o JSON atualizado
    with open(dest_file, 'w') as f:
        json.dump(data, f, indent=4)
