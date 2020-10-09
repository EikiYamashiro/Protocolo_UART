#####################################################
# Camada Física da Computação
#Carareto
#28/08/2020
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 
#ALGUNS ARDUINOS PRECISAM FICAR COM O BOTAO DE RESET PRESSIONADO. OU O PINO RESET ATERRADO!

from enlace import *
import time

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)


# se fosse apenas o arduino, uma porta de comunicaçã seria suficiente, estamos usando duas pq o software de emular recebe um uma porta e envia em outra
serialName1 = "COM1"
serialName2 = "COM2"                  # Windows(variacao de)


def main():
    try:
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName1)
        com2 = enlace(serialName2)
        print('declarou enlace')
    
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()
        com2.enable()
        print('habilitou com')
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        
       
        imageR = "./imageB.png"
         # Endereco da imagem a ser salva
        imageW = "./recebidaTeste.png"

        # Log
        print("-------------------------")
        print("Comunicação inicializada")
        print("  porta : {}".format(com1.fisica.name))
        print("-------------------------")


        #aqui você deverá gerar os dados a serem transmitidos. 
        #seus dados a serem transmitidos são uma lista de bytes a serem transmitidos. Gere esta lista com o 
        #nome de txBuffer. Esla sempre irá armazenar os dados a serem enviados.
       
        # Carrega imagem
        print ("Carregando imagem para transmissão :")
        print (" - {}".format(imageR))
        print("-------------------------")
        txBuffer = open(imageR, 'rb').read()
       
               
        #faça aqui uma conferência do tamanho do seu txBuffer, ou seja, quantos bytes serão enviados.
        print(len(txBuffer))

        
        
        
        #finalmente vamos transmitir os tados. Para isso usamos a funçao sendData que é um método da camada enlace.
        #faça um print para avisar que a transmissão vai começar.
        #tente entender como o método send funciona!
        com1.sendData(txBuffer)
        print('enviou')

        # A camada enlace possui uma camada inferior, TX possui um método para conhecermos o status da transmissão
        # Tente entender como esse método funciona e o que ele retorna
        time.sleep(0.5) #sem o time o getStatus retorna zero, pois nao deu tempo de enviar
        txSize = com1.tx.getStatus()
        print('tamanho do que enviou {}' .format(txSize))
        #Uma outra forma de saber o tamanho da lista enviada é apenas fazendo:
        txSize = len(txBuffer) #modo alternativo... mais simples, mas se nem todos os bytes foram realmente enviados, havera problemas
        
        #Agora vamos iniciar a recepção dos dados. Se algo chegou ao RX, deve estar automaticamente guardado
        #Observe o que faz a rotina dentro do thread RX
        #print um aviso de que a recepção vai começar.
        #Será que todos os bytes enviados estão realmente guardadas? Será que conseguimos verificar?
        #Veja o que faz a funcao do enlaceRX  getBufferLen
        #acesso aos bytes recebidos
        
        
        #IMPORTANTE: se voce obteve o tamnho do txBuffer com o getStatus, tem que transformar o tamanho em int para poder usar no getData. (A funcao getStatus retorna em float)
        #int(txSize)...
        rxBuffer, nRx = com2.getData(txSize)
        print('recebeu {} bytes de dados' .format(len(rxBuffer)))
    
    
          # Salva imagem recebida em arquivo
        print("-------------------------")
        print ("Salvando dados no arquivo :")
        print (" - {}".format(imageW))
        f = open(imageW, 'wb')
        f.write(rxBuffer)

    # Fecha arquivo de imagem
        f.close()     
    
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        com2.disable()
    except:
        print("ops! :-\\")
        com1.disable()
        com2.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
