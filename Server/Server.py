  
#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação Server
####################################################

from enlace import enlace
import time
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import crcmod
import logging
logging.basicConfig(filename='server_2.log', filemode='w', format='CLIENT - %(asctime)s - %(message)s', level=logging.INFO)

#EOP definido como 2304:
eop = (2304).to_bytes(4, 'big')

#idClient
idClient = (39).to_bytes(1, 'big')

#idServer
idServer= (1).to_bytes(1, 'big')

#idArquivo
idArquivo = (1).to_bytes(1, 'big')

#CRC
CRC = (1).to_bytes(2, 'big')

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

#last_package
last_package = 0

def getPayload(datagrama):
    return datagrama[10:-4]

def getEop(datagrama):
    return datagrama[-4:]


def create_head_4(contador, sizeMensagem, sizePayload, tipoMensagem, restart):
    head = tipoMensagem + idClient + idServer + sizeMensagem + contador + sizePayload + restart + success + CRC
    return head

def create_head(contador, sizeMensagem, sizePayload, tipoMensagem):
    if tipoMensagem == tipo1:
        head = tipoMensagem + idClient + idServer + sizeMensagem + contador + idArquivo + restart + success + CRC
    else:
        head = tipoMensagem + idClient + idServer + sizeMensagem + contador + sizePayload + restart + success + CRC
    return head

def create_tipo2():
    head = create_head((0).to_bytes(1, 'big'), (0).to_bytes(1, byteorder='big'), (0).to_bytes(1, byteorder='big'), tipo2)
    datagrama = head + eop
    return datagrama

def create_tipo4(last_package):
    head = tipo4 + (0).to_bytes(5, 'big') +  success + last_package + CRC
    datagrama = head + eop
    return datagrama

def create_tipo5():
    head = tipo5 + (0).to_bytes(9, 'big')
    datagrama = head + eop
    return datagrama

def create_tipo6(h6, h7):
    head = tipo6 + (0).to_bytes(5, 'big') + h6.to_bytes(1, 'big') + h7 + CRC
    datagrama = head + eop
    return datagrama

def getHead(datagrama):
    return datagrama[:10]

eop = (2304).to_bytes(4, 'big')

confirm_msg = (29).to_bytes(1, 'big')
error_msg = (5).to_bytes(1, 'big')

def error_print():
    print("---------------------------------")
    print("---------------------------------")
    print("-------------ERROR---------------")
    print(' ')
    print("TAMANHO DO PAYLOAD DO HEAD DIFERENTE DO RECEBIDO!!!")
    print(' ')
    print("-------------ERROR---------------")
    print("---------------------------------")
    print("---------------------------------")

def main():
    try:
        crc16_func = crcmod.mkCrcFun(0x11021, initCrc=0, xorOut=0xFFFFFFFF)
        
        msg_error = "Comunicação sem erros!"
        com2 = enlace('COM3')
        com2.enable() 
        print("Server disponível")
        logging.info(f"SERVER DISPONÍVEL")
        com2.rx.getIsEmpty()
        #----------------------GET--HANDSAHKE-------------------------
        handshake_recebido, nRx = com2.getData(14)
        logging.info(f"RECEBIDO | TIPO: 1 | TAMANHO: 14")
        head_handshake = getHead(handshake_recebido)
        id_handshake = head_handshake[2]
        tipo_handshake = head_handshake[0]
        quant_handshake = handshake_recebido[3]
        id_arquivo = head_handshake[5] 
        
        print("-------------------------------------")
        print("Convite para Transmissão Recebido!")
        print("ID do server de destino: {}".format(id_handshake))
        print("Tipo da Mensagem: {}".format(tipo_handshake))
        print("Quantidade de pacotes do Arquivo de ID {0}: {1} pacotes".format(id_arquivo, quant_handshake))
        real_size_mensagem = getHead(handshake_recebido)[3]
        print("-------------------------------------")
        print(" ")
        com2.sendData(create_tipo2())
        logging.info(f"ENVIADO | TIPO: 2 | TAMANHO: 14")
        imageW = "recebidaCopia.png"
        list_payload = []
        verifica_id = 1
        antecede_number = 0
        last_package = 0
        while True:
            error = False
            #----------------------GET--HEAD--------------------------
            head = com2.rx.getNOnTime(10, 10)
            logging.info(f"RECEBIDO HEAD| TIPO: 3 | TAMANHO: 10 | PACOTE: {head[4]} | TOTAL PACOTES: {head[3]} | CRC: {head[8:]}")
            if head == False:
                print("Tempo esgotado")
                com2.sendData(create_tipo5())
                break
            print("Recebendo HEAD do Client...")
            print("Tipo da Mensagem: {}".format(head[0]))
            sizePayload = head[5]
            sizeMensagem = head[3]
            numeroPacote = head[4]
            crc_recebido = head[8:]
           
            print("sizeMensagem: {}".format(sizeMensagem))
            print("numeroPacote: {}".format(numeroPacote))
            print("sizePayload: {}".format(sizePayload))
            print("---------------------------------")
            if verifica_id != numeroPacote:
                print("Pacote {}: Erro na ordem dos pacotes".format(verifica_id))
                error = True
            #---------------------GET--PAYLOAD-------------------------
            print("Recebendo PAYLOAD do Client...")
            print("---------------------------------")
            payload, nRx = com2.getData(sizePayload)
            crc_check = crc16_func(payload).to_bytes(2, "big")
            if error != True:
                logging.info(f"RECEBIDO PAYLOAD| TIPO: 3 | TAMANHO: {head[5]} | PACOTE: {head[4]} | TOTAL PACOTES: {head[3]} | CRC: {crc_recebido}")
            
            if crc_check != crc_recebido:
                print("Pacote {}: CRCs Diferentes!".format(verifica_id))
                error = True
            else: 
                if error != True:
                    list_payload.append(payload)
            #-----------------------GET--EOP---------------------------
            eop, nRx = com2.getData(4)
            print("Recebendo EOP do Client...")
            print("---------------------------------")
            if error != True:
                logging.info("RECEBIDO EOP | TIPO: 3 | TAMANHO: 4")
            time.sleep(0.5)
            print(" ")
            print(" ")
            
            if eop != b'\x00\x00\t\x00':
                break
            if error == True:
                com2.sendData(create_tipo6(verifica_id, (last_package).to_bytes(1, 'big')))
                logging.info("ENVIADO | TIPO: 6 | TAMANHO: 14")
                print(verifica_id)
            else:
                last_package = int(numeroPacote)
                com2.sendData(create_tipo4((last_package).to_bytes(1, 'big')))
                logging.info("ENVIADO | TIPO: 4 | TAMANHO: 14")
                verifica_id += 1
            time.sleep(2)
            if sizeMensagem == numeroPacote:
                break
           
        
        
        mensagem = b''.join(list_payload)  
        f = open(imageW, 'wb')
        f.write(mensagem)
        f.close()
        
        print(msg_error)
        print("-------------------------------------")
        print("Comunicação encerrada")
        print("-------------------------------------")
        com2.disable()  
    except Exception as e:
        print(e)
        print("ops! :-\\")
        com2.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()