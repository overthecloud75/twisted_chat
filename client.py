import socket
import select
import sys
import threading

name = None

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 8000))
i = 0


def get_msg():
    data = s.recv(4096)  # 4096바이트를 읽음.
    global name
    if name is None:  # 처음 접속시 부여 받은 이름을 저장!
        name = data.decode()
        s.send(f'{name} is connected!'.encode('utf-8'))  # 다른 사람에게 접속 사실을 알리게 됩니다.
    else:
        print(f"{data.decode('utf-8')}")  # byte -> string 출력


if sys.platform == 'win32':
    def get_stdin():
        while True:
            desc = sys.stdin
            msg = desc.readline()  # 사용자의 입력 문자열을 읽어 서버에 전송함
            msg = msg.replace('\n', '')  # 사용자의 입력 문자열을 읽어 서버에 전송함
            s.send(f'{name}: {msg}'.encode())

    t1 = threading.Thread(target=get_stdin)
    t1.daemon = True
    t1.start()
    while True:  # 서버로부터 메시지를 기다림
        # OSError: [WinError 10038] sys.stdin이 socket이 아니어서 error 발생한다고 함
        # https://stackoverflow.com/questions/25071008/python-sock-chat-client-problems-with-select-select-and-sys-stdin
        read = select.select([s], [], [], 1)[0]
        # read, write, fail = select.select([s, socket.socket()], [], [])
        if read:
            get_msg()
else:
    while True:
        read, write, fail = select.select([s, sys.stdin], [], [])
        # socket에서 메시지를 읽을수 있을 때까지 대기
        # sys.stdin은 사용자가 키보드 엔터를 입력 할 때까지 기다림
        for desc in read:  # 메시지가 도착하면
            if desc == s:  # 만약 서버에서 온 메시지라면 출력
                get_msg()
            else:  # 만약 사용자가 입력한 메시지라면
                msg = desc.readline()  # 사용자의 입력 문자열을 읽어 서버에 전송함
                msg = msg.replace('\n', '')  # 사용자의 입력 문자열을 읽어 서버에 전송함
                s.send(f'{name}: {msg}'.encode())
# reference
# https://velog.io/@hyeseong-dev/%EC%86%8C%EC%BC%93%ED%86%B5%EC%8B%A0-%ED%8C%8C%EC%9D%B4%EC%8D%AC-%EC%B1%84%ED%8C%85%EC%95%B1
