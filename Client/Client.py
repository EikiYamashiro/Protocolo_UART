  
#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação Client
####################################################

from enlace import enlace
import time
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import math
import crcmod
import logging
logging.basicConfig(filename='client_3.log', filemode='w', format='CLIENT - %(asctime)s - %(message)s', level=logging.INFO)

zero_bytes = (0).to_bytes(1, 'big')

#EOP definido como 2304:
eop = (2304).to_bytes(4, 'big')

#idClient
idClient = (39).to_bytes(1, 'big')

#idServer
#idServer = (int(input("Server ID: "))).to_bytes(1, 'big')
idServer = (1).to_bytes(1, 'big')

#idArquivo
idArquivo = (1).to_bytes(1, 'big')

#CRC
CRC_fake = (1).to_bytes(2, 'big')

#success
success = (1).to_bytes(1, 'big')

#restart
restart = (1).to_bytes(1, 'big')

#TIPO 1: Chamado do cliente convidando o server para uma transmissão! Precisamos enviar o id do server para confirmar que o destino da imagem!
tipo1 = (1).to_bytes(1, 'big')

#TIPO 2: Mensagem enviado do serviddor ao cliente  confirmando que o server está ocioso!
tipo2 = (2).to_bytes(1, 'big')

#TIPO 3: Mensagem de dados. Contém o Payload
tipo3 = (3).to_bytes(1, 'big')

#TIPO 4: Server envia confirmação que tipo3 foi recebido 
tipo4 = (4).to_bytes(1, 'big')

#TIPO 5: Mensagem de time out
tipo5 = (5).to_bytes(1, 'big')

#TIPO 6: Mensagem de erro. Server envia uma mensagem informando que houve um erro!
tipo6 = (6).to_bytes(1, 'big')

def getHead(datagrama):
    return datagrama[:10]

def getPayload(datagrama):
    return datagrama[10:-4]

def getEop(datagrama):
    return datagrama[-4:]

def create_handshake(size_arquivo):
    head = create_head((0).to_bytes(1, 'big'), size_arquivo, (0).to_bytes(1, byteorder='big'), tipo1, CRC_fake)
    datagrama = head + eop
    return datagrama



def create_head(contador, sizeMensagem, sizePayload, tipoMensagem, crc):
    if tipoMensagem == tipo1:
        head = tipoMensagem + idClient + idServer + sizeMensagem + contador + idArquivo + restart + success + CRC_fake
    else:
        head = tipoMensagem + idClient + idServer + sizeMensagem + contador + sizePayload + restart + success + crc
    return head
    

def create_datagram_list(mensagem):
    datagrama = []
    c_total = 0
    contador = 0
    ID = 1
    sizeMensagem_int = math.ceil(len(mensagem)/114)
    sizeMensagem = sizeMensagem_int.to_bytes(1, byteorder='big')
    dg_list = []
    crc16_func = crcmod.mkCrcFun(0x11021, initCrc=0, xorOut=0xFFFFFFFF)
    #Cada rodada cria um novo payload
    while c_total < len(mensagem)-1:
        
        if len(mensagem)-contador < 114:
            payload = mensagem[contador:]
            crc = crc_out = crc16_func(payload).to_bytes(2, "big")
            head = create_head(ID.to_bytes(1, 'big'), sizeMensagem, len(payload).to_bytes(1, byteorder='big'), tipo3, crc)
            datagrama = head + payload + eop
            dg_list.append(datagrama)
            ID += 1
            break
        else:
            payload = mensagem[0+contador:114+contador]
            crc = crc_out = crc16_func(payload).to_bytes(2, "big")
            head = create_head(ID.to_bytes(1, 'big'), sizeMensagem, len(payload).to_bytes(1, byteorder='big'), tipo3, crc)
            
            datagrama = head + payload + eop
            contador += 114
            ID += 1
            
        #Adiciona o datagrama na lista de datagramas
        dg_list.append(datagrama)
        
        #Zera os valores das variaveis
        playload = []
        head = []
        datagrama = []
        
        
    return dg_list

def main():
    try:
        
        #Abre a interface para o usuário selecionar a imagem
       #print('Escolha uma imagem:')
       #Tk().withdraw()
        #image_selected = askopenfilename(filetypes=[("Image files", ".png .jpg .jpeg")])
        #print("Imagem selecionada: {}".format(image_selected))
        print("Imagem selecionada: {}".format("C:/Users/eikis/OneDrive/Área de Trabalho/oiakon.png"))
        image_selected = "C:/Users/eikis/OneDrive/Área de Trabalho/oiakon.png"
        
        #Carrega imagem para transmissão
        print("Carregando imagem para transmissao...")
        print("-----------------------------------")
        txBufferClient = open(image_selected, 'rb').read()
        size_real = len(txBufferClient)
        txSizeClient = len(txBufferClient).to_bytes(4, byteorder='big')
        print("Criando datagramas...")
        datagrama_list = create_datagram_list(txBufferClient)
        print("Lista de datagramas criada com sucesso!")
        
        size_arquivo = getHead(datagrama_list[0])[3]
        print("Número Total de pacotes do arquivo: {} pacotes".format(size_arquivo))
        handshake = create_handshake(size_arquivo.to_bytes(1, 'big'))
        print("ENVIANDO HANDSHAKE")
        t = True
        while t==True:
            com1 = enlace('COM4') 
            com1.enable()
            com1.sendData(handshake)
            logging.info("ENVIADO | TIPO: 1 | TAMANHO: 14")
            handshake_recebido = com1.rx.getNOnTime(14, 5)
            if  handshake_recebido == False:
                resp = input("Servidor inativo. Tentar novamente? S/N")
                if resp == "N":
                    s
                elif resp=="S":
                    com1.disable()
            else:
                t = False
                print("HANDSHAKE RECEBIDO")
                logging.info("RECEBIDO | TIPO: 2 | TAMANHO: 14")
                print("Tipo do Handshake: {}".format(handshake_recebido[0]))
        print("-----------------------------------")
        fake = True 
        i = 0
        while i < len(datagrama_list):
            if i==0:
                print("-")
            else:
                 confirmacao_server = com1.rx.getNOnTime(14, 20)
                 head_server = getHead(confirmacao_server)
                 if head_server[0].to_bytes(1, 'big') == tipo4: 
                     print("Ultimo pacote recebido pelo servidor com sucesso: {}".format(head_server[7]))
                     logging.info(f"RECEBIDO | TIPO: 4 | TAMANHO: 14 | ULTIMO PACOTE RECEBIDO PELO SERVIDOR COM SUCESSO: {head_server[7]}")
                 if head_server[0].to_bytes(1, 'big') == tipo5:
                     print("Tempo de comunicação esgotado, fechando comunicação com server...")
                     logging.info("RECEBIDO | TIPO: 5 | TAMANHO: 14")
                     break
                 if head_server[0].to_bytes(1, 'big') == tipo6:
                     print("Pacote {} não recebido pelo servidor com sucesso!".format(head_server[6]))
                     logging.info("RECEBIDO | TIPO: 6 | TAMANHO: 14")
                     i = head_server[6] - 1
                 if head_server == False:
                     print("Ausência de resposta de pacote de dados recebido, por mais de 20 segundos")
                     break
            print("i: ", i)     
            datagrama = datagrama_list[i]
            head = getHead(datagrama)
            payload = getPayload(datagrama)
            eop = getEop(datagrama)
            i += 1  
            print("Enviando Pacote {} para o Servidor...".format(head[4]))
            print("-----------------------------------")
            #---------------------SEND--HEAD-------------------------
            com1.sendData(head)
            logging.info(f"ENVIADO HEAD| TIPO: 3 | TAMANHO: 10 | PACOTE: {head[4]} | TOTAL PACOTES: {head[3]} | CRC: {head[8:]}")
            time.sleep(0.5)                     
            #-------------------SEND--PAYLOAD------------------------
            com1.sendData(payload)
            logging.info("ENVIADO PAYLOAD | TIPO: 3 | TAMANHO: {}".format(head[5]))
            time.sleep(0.5)
            #---------------------SEND--EOP--------------------------
            com1.sendData(eop)
            logging.info("ENVIADO EOP | TIPO: 3 | TAMANHO: 4")
            time.sleep(0.5)
                
        confirmacao_server = com1.rx.getNOnTime(14, 20)
        head_server = getHead(confirmacao_server)
        if head_server[0].to_bytes(1, 'big') == tipo4: 
            print("Ultimo pacote recebido pelo servidor: {}".format(head_server[7]))
            logging.info(f"RECEBIDO | TIPO: 4 | TAMANHO: 14 | ULTIMO PACOTE RECEBIDO PELO SERVIDOR COM SUCESSO: {head_server[7]}")
                             
        print("Todos Pacotes Enviados!")
        
        # Encerra comunicação
        com1.disable()
        print("-----------------------------------")
        print("Comunicação encerrada!")
        print("-----------------------------------")
    except Exception as e:
        print(e)
        print("ops! :-\\")
        com1.disable()

if __name__ == "__main__":
    main()