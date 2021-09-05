import names  # Random name generator
from twisted.internet import protocol, reactor  # 네트워크 통신을 쉽게 구현 하도록 도와주는 패키지

transports = []
users_dict = {}


class Chat(protocol.Protocol):
    def __init__(self, addr):
        self.addr = addr

    # 채팅 서버의 로직 정의
    def connectionMade(self):
        # 사용자가 서버에 접속하면 'connected'
        print(f'{self.transport} is connectd')
        name = names.get_first_name()
        if self.transport not in transports:
            transports.append(self.transport)  # 사용자가 접속하면 transport(클라이언트)추가
            users_dict[str(self.transport)] = {}
            users_dict[str(self.transport)]['name'] = name
            users_dict[str(self.transport)]['addr'] = self.addr
            self.transport.write(f'{name}'.encode('utf-8'))
            # name은 사용자가 접속하면 임의의 이름을 부여함.
            # client 연결시, client에게 name을 전달

    # https://stackoverflow.com/questions/16087768/how-do-i-check-if-a-twisted-internet-protocol-instance-has-disconnected
    def connectionLost(self, reason):
        print(f"{users_dict[str(self.transport)]['name']} is disconnectd : {reason}")
        transports.remove(self.transport)
        for t in transports:
            t.write(f"{users_dict[str(self.transport)]['name']} is disconnected".encode('utf-8'))
        del users_dict[str(self.transport)]

    def dataReceived(self, data):
        # 사용자가 서버에 메시지를 보내면 실행 사용자 메시지(data) 출력'
        print(f"{users_dict[str(self.transport)]['name']} : {data.decode('utf-8')}")
        for t in transports:  # 모든 클라이언트를 하나씩 돌면서 만약 내가 보낸 메시지가 아니면 메시지를 전달함
            if self.transport is not t:
                t.write(data)


class ChatFactory(protocol.Factory):
    # 통신 프로토콜 정의
    def buildProtocol(self, addr):
        print('addr', addr)
        return Chat(addr)


if __name__ == '__main__':
    print('server started')
    reactor.listenTCP(8000, ChatFactory())
    # endpoints.serverFromString(reactor, 'tcp:8000').listen(EchoFactory())
    reactor.run()
