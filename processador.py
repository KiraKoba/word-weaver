import os
import io
import base64
import docx
import glob
import shutil
from PIL import Image
from langchain_ollama.llms import OllamaLLM
from deep_translator import GoogleTranslator # --- NOVO ---
from langdetect import detect, LangDetectException  # --- NOVO ---

# --- CONSTANTES E CONFIGURAÇÕES ---
INPUT_DIRECTORY = "input"
OUTPUT_DIRECTORY = "output"
IMAGE_TEMP_DIR = "imagens_temp_processador"
OLLAMA_MODEL = "llava-phi3" 

# --- FUNÇÕES AUXILIARES ---

def image_to_base64(image_path):
    """Converte um arquivo de imagem para uma string base64, usando 'with' para segurança."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        print(f"   > AVISO: Não foi possível ler o arquivo de imagem {image_path}: {e}")
        return None

# --- NOVA FUNÇÃO DE TRADUÇÃO ---
def traduzir_se_necessario(texto, idioma_alvo='pt'):
    """
    Detecta o idioma do texto. Se for inglês, traduz para o idioma alvo (português).
    """
    try:
        # Detecta o idioma do texto
        idioma_detectado = detect(texto)
        
        # Se o idioma detectado for inglês, realiza a tradução
        if idioma_detectado == 'en':
            print(f"   > Descrição detectada em inglês. Traduzindo para '{idioma_alvo}'...")
            tradutor = GoogleTranslator(source='en', target=idioma_alvo)
            texto_traduzido = tradutor.translate(texto)
            return texto_traduzido
            
    except LangDetectException:
        # Ocorre se o texto for muito curto ou ambíguo para detecção
        print("   > AVISO: Não foi possível detectar o idioma da descrição. Mantendo original.")
    except Exception as e:
        print(f"   > ERRO ao tentar traduzir o texto: {e}. Mantendo original.")
        
    # Retorna o texto original se não for inglês ou se ocorrer um erro
    return texto

def get_image_description_ollama(model, image_path, context_text=""):
    """
    Usa um modelo Ollama (como o LLaVA) para gerar a descrição de uma imagem.
    """
    image_b64 = image_to_base64(image_path)
    if not image_b64:
        return "[ERRO AO LER ARQUIVO DE IMAGEM]"
        
    try:
        llm_with_images = model.bind(images=[image_b64])
        
        prompt = (
            "Esta é uma captura de tela de uma interface de software. Sua tarefa é descrevê-la para um manual. "
            "Primeiro, leia todo o texto visível na imagem, incluindo menus, nomes de pastas e botões. "
            "Depois, descreva a estrutura geral da tela. "
            f"O texto do manual que acompanha esta imagem é: '{context_text}'. Use isso para focar sua descrição no que é mais relevante. Lembre-se que a resposta deve ser em português."
        )
        
        print(f"   > Analisando imagem '{os.path.basename(image_path)}' com {OLLAMA_MODEL}...")
        descricao_original = llm_with_images.invoke(prompt)
        
        # --- MODIFICADO: Adiciona a etapa de verificação e tradução ---
        descricao_final = traduzir_se_necessario(descricao_original)
        
        return descricao_final.strip()
        
    except Exception as e:
        print(f"   > ERRO DETALHADO ao tentar usar o LLaVA:")
        print(f"   > Tipo do Erro: {type(e).__name__}")
        print(f"   > Mensagem: {e}")
        return "[ERRO NA ANÁLISE DA IMAGEM]"

def process_docx_to_markdown(model, input_path, output_path):
    """
    Função principal que lê um DOCX, processa texto e imagens, e escreve um MD.
    """
    print("-" * 60)
    print(f"Iniciando processamento do arquivo: '{input_path}'")

    doc = docx.Document(input_path)
    markdown_content = []
    image_map = {}
    img_counter = 0

    for rel in doc.part.rels:
        if "image" in doc.part.rels[rel].target_ref:
            img_counter += 1
            image_part = doc.part.rels[rel].target_part
            image_blob = image_part.blob
            
            try:
                image = Image.open(io.BytesIO(image_blob))
                ext = image.format.lower() if image.format else 'png'
            except Exception:
                ext = 'png'

            temp_image_path = os.path.join(IMAGE_TEMP_DIR, f"temp_image_{img_counter}.{ext}")
            with open(temp_image_path, "wb") as f:
                f.write(image_blob)
            
            image_map[doc.part.rels[rel].rId] = temp_image_path

    last_text = ""
    for p in doc.paragraphs:
        if 'graphicData' in p._p.xml:
            for rId in image_map:
                if rId in p._p.xml:
                    image_path = image_map[rId]
                    description = get_image_description_ollama(model, image_path, context_text=last_text)
                    markdown_content.append(f"\n> **[Descrição da Imagem]**: {description}\n")
                    break
        else:
            text = p.text.strip()
            if text:
                if p.style.name.startswith('Heading 1'):
                    markdown_content.append(f"# {text}")
                elif p.style.name.startswith('Heading 2'):
                    markdown_content.append(f"## {text}")
                elif p.style.name.startswith('Heading 3'):
                    markdown_content.append(f"### {text}")
                else:
                    markdown_content.append(text)
                last_text = text

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(markdown_content))
    
    print(f"✅ Processamento concluído!")
    print(f"📄 Arquivo de saída salvo em: '{output_path}'")

def main():
    """
    Função principal que orquestra o processamento em lote.
    """
    os.makedirs(INPUT_DIRECTORY, exist_ok=True)
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    
    if os.path.exists(IMAGE_TEMP_DIR):
        shutil.rmtree(IMAGE_TEMP_DIR)
    os.makedirs(IMAGE_TEMP_DIR)

    print("Iniciando o modelo Ollama... (isso pode levar um momento)")
    try:
        ollama_llava = OllamaLLM(model=OLLAMA_MODEL)
    except Exception as e:
        print(f"ERRO: Não foi possível inicializar o modelo Ollama ('{OLLAMA_MODEL}').")
        print(f"Verifique se o aplicativo Ollama está em execução e se o modelo foi baixado com 'ollama pull {OLLAMA_MODEL}'.")
        return

    docx_files = glob.glob(os.path.join(INPUT_DIRECTORY, "*.docx"))

    if not docx_files:
        print(f"Nenhum arquivo .docx encontrado no diretório '{INPUT_DIRECTORY}'.")
        return

    print(f"Encontrados {len(docx_files)} arquivos para processar.")
    processed_count = 0

    for input_file_path in docx_files:
        base_name = os.path.basename(input_file_path)
        file_name_without_ext = os.path.splitext(base_name)[0]
        output_file_path = os.path.join(OUTPUT_DIRECTORY, f"{file_name_without_ext}.md")
        
        ### NOVO: Bloco de verificação para pular arquivos já processados ###
        if os.path.exists(output_file_path):
            print("-" * 60)
            print(f"AVISO: Arquivo '{os.path.basename(output_file_path)}' já existe. Pulando.")
            continue # Pula para o próximo arquivo da lista
        
        process_docx_to_markdown(ollama_llava, input_file_path, output_file_path)
        processed_count += 1

    try:
        shutil.rmtree(IMAGE_TEMP_DIR)
    except OSError as e:
        print(f"AVISO: Não foi possível limpar a pasta temporária '{IMAGE_TEMP_DIR}'. Erro: {e}")

    print("-" * 60)
    if processed_count > 0:
        print(f"✨ {processed_count} novo(s) arquivo(s) foi(ram) processado(s) com sucesso! ✨")
    else:
        print("✨ Nenhum arquivo novo para processar. Tudo já está atualizado! ✨")


if __name__ == "__main__":
    main()