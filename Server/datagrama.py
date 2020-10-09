

class Datagrama():
    
    def __init__(self, txBufferClient):
        self.head = []
        self.playload = []
        self.eop = []
        i = 0
        while i < len(txBufferClient):
            if i < 10:
                self.head.append(txBufferClient[i])
            elif i < len(txBufferClient) and i < (len(txBufferClient)-5):
                self.eop.append(txBufferClient[i])
            else:
                self.playload.append(txBufferClient[i])
                
        