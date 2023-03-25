import logging

from websocket_server import WebsocketServer


def join_room(req: dict) -> dict:
    return

def create_room(req: dict) -> dict:
    return

def end_code_phase(req: dict) -> dict:
    return

def end_answer_phase(req: dict) -> dict:
    return

def open_next_result(req: dict) -> dict:
    return

def user_id(req: dict) -> dict:
    return

def start_game(req: dict) -> dict:
    return

def main():
    def new_client(client: dict, server: WebsocketServer):
        print(f'新規クライアントが ID={client["id"]} で接続しました')
        server.send_message_to_all('Hey all, a new client has joined us')
        return

    def client_left(client: dict, server: WebsocketServer):
        print(f'ID={client["id"]} が切断されました')
        return

    def message_received(client: dict, server: WebsocketServer, message: str):
        print(f'ID={client["id"]} から "{message}" を受信しました')
        # TODO:
        # 1. message (JSON な文字列) をデコードする (dict が得られるはず)
        # 2. type に応じて適当な関数を呼び出す
        # 3. 返ってきた dict を JSON にエンコード
        # 4. send_message する
        return

    server = WebsocketServer(host='127.0.0.1', port=9001, loglevel=logging.DEBUG)
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    server.run_forever()
    return

if __name__ == '__main__':
    main()
