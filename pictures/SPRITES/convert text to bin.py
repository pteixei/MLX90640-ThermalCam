import time

def rgb_to_rgb565(r, g, b):
    r_5bit = (r >> 3) & 0x1F  # 5 bits para R
    g_6bit = (g >> 2) & 0x3F  # 6 bits para G
    b_5bit = (b >> 3) & 0x1F  # 5 bits para B
    # Compacta os valores em 2 bytes (16 bits)
    return (r_5bit << 11) | (g_6bit << 5) | b_5bit

def processar_arquivo_txt(filename):
    chunk_size = 2048  # Tamanho do pedaço a ser lido (em bytes)

    with open(filename + ".txt", "r") as f, open(filename + ".bin", "wb") as bin_f:
        buffer = ""  # Buffer para armazenar dados incompletos entre os chunks
        chunks = 0

        while True:
            chunk = f.read(chunk_size)  # Lê um pedaço do arquivo
            if not chunk:
                break  # Sai do loop ao chegar no final do arquivo
            
            chunks += 1

            # Adiciona o chunk ao buffer
            buffer += chunk

            # Separa os números por vírgula
            parts = buffer.split(",")

            # Mantém o último elemento no buffer, pois pode estar incompleto
            buffer = parts.pop()

            # Converte os números válidos para inteiros e grava no arquivo binário
            try:
                valores_int = [int(v.strip()) for v in parts if v.strip().isdigit() and 0 <= int(v.strip()) <= 255]
                bin_f.write(bytearray(valores_int))
            except ValueError:
                print(f"Erro ao converter valores no chunk {chunks}. Ignorando.")

            print(f"{chunks} chunks processados. {len(valores_int)} valores escritos.")

        # Processa o restante do buffer após o loop
        if buffer.strip():  # Garante que não está vazio
            print("Registros sobrantes encontrados no buffer.")
            try:
                n = int(buffer.strip())
                if 0 <= n <= 255:
                    bin_f.write(bytearray([n]))
                    print("Valor sobrante gravado:", n)
            except ValueError:
                print("Erro ao processar valor sobrante. Ignorando.")

    print(f"Ficheiro {filename}.bin criado com sucesso.")
    
def processar_arquivo_txt_ori(filename):
    chunk_size = 2048  # Tamanho do pedaço a ser lido (em bytes)
#     try:
        
    with open(filename + ".txt", "r") as f, open(filename + ".bin", "wb") as bin_f:
        buffer = ""  # Buffer para armazenar dados incompletos entre os chunks
        chunks = 0
        while True:
            chunk = f.read(chunk_size)  # Lê um pedaço do arquivo
            print(f"Chunk lido: {chunk}")	
            if not chunk:
                break  # Sai do loop ao chegar no final do arquivo
            
            chunks += 1
            
            # Adiciona o chunk ao buffer
            buffer += chunk
            print(f"Buffer após leitura: {buffer}")

            # Separa os números por vírgula
            parts = buffer.split(",")
            print(f"Partes separadas: {parts}")

            # Mantém o último elemento no buffer, pois pode estar incompleto
            buffer = parts.pop()
            print(f"Última parte incompleta no buffer: {buffer}")

            # Converte os números válidos para inteiros e grava no arquivo binário
            valores_int = [int(v) for v in parts if v.isdigit() and 0 <= int(v) <= 255]
            bin_f.write(bytearray(valores_int))
            print(f"Valores convertidos: {valores_int}")

        # Processa o restante do buffer após o loop
        if buffer.strip():  # Garante que não está vazio
            print("Registos sobrantes")
            try:
                n = int(buffer.strip())
                if 0 <= n <= 255:
                    print("Registos sobrantes escritos em ", filename + ".bin")

                    bin_f.write(bytearray([n]))
            except ValueError:
                pass  # Ignora valores inválidos no final

    
    print(f"Ficheiro {filename}.bin criado.")

def rgb_get(arquivo):
    import struct

    tamanho_framebuffer = 96 * 40  # Número de pixels esperados

    with open(arquivo + ".bin", "rb") as f, open(arquivo + "565.bin", "wb") as f565:
        for _ in range(tamanho_framebuffer):
            # Lê 3 bytes (R, G, B)
            rgb = f.read(3)
            if len(rgb) < 3:
                break  # Sai do loop se não houver bytes suficientes
            # Desempacota os valores de R, G e B
            red, green, blue = struct.unpack("BBB", rgb)
            # Converte R, G, B para RGB565
            rgb565 = rgb_to_rgb565(red, green, blue)
            # Escreve no arquivo no formato de 16 bits
            f565.write(struct.pack("H", rgb565))


filenames = ["Button bottom", "Button left-bottom","Button left-top","Button right-bottom","Button right-top","Button top","button_full_ok_bottom", "button_full_ok_top"]
read_path = "./TXT/"
write_path = "./BIN/"
for filename in filenames:
#    processar_arquivo_txt(read_path+filename)
    rgb_get(write_path+filename)
