import os

# Mapeamento das substituições
substitutions = {
    "groceries": "insumo",
    "houses": "rendimento",
    "iris": "saude_lavoura"
}

# Diretório principal do projeto
base_directory = "/caminho/para/seu/projeto"

# Função para renomear pastas e arquivos
def rename_dirs_and_files(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        # Renomear arquivos
        for filename in files:
            new_filename = filename
            for old_value, new_value in substitutions.items():
                new_filename = new_filename.replace(old_value, new_value)
            if new_filename != filename:
                old_path = os.path.join(root, filename)
                new_path = os.path.join(root, new_filename)
                os.rename(old_path, new_path)
                print(f"Renomeado arquivo: {old_path} -> {new_path}")

        # Renomear pastas
        for dirname in dirs:
            new_dirname = dirname
            for old_value, new_value in substitutions.items():
                new_dirname = new_dirname.replace(old_value, new_value)
            if new_dirname != dirname:
                old_path = os.path.join(root, dirname)
                new_path = os.path.join(root, new_dirname)
                os.rename(old_path, new_path)
                print(f"Renomeada pasta: {old_path} -> {new_path}")

# Função para substituir strings nos arquivos
def replace_in_files(directory):
    for root, _, files in os.walk(directory):
        for filename in files:
            # Processar apenas arquivos de código (ajuste as extensões conforme necessário)
            if filename.endswith((".py", ".json", ".txt")):
                file_path = os.path.join(root, filename)
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()

                # Fazer as substituições
                updated_content = content
                for old_value, new_value in substitutions.items():
                    updated_content = updated_content.replace(old_value, new_value)

                # Salvar apenas se houver mudanças
                if updated_content != content:
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(updated_content)
                    print(f"Atualizado arquivo: {file_path}")

# Renomear pastas e arquivos
rename_dirs_and_files(base_directory)

# Substituir strings no conteúdo dos arquivos
replace_in_files(base_directory)

print("Processo concluído!")