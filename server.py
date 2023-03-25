import logging
import json
import uuid #print(uuid.uuid1())
from websocket_server import WebsocketServer


# TODO:
# message_received で使う関数を生やす
# dict でやりとりする? (JSON との変換は message_received の方でやる)
def userId_request(req: dict) -> dict:
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
        data = json.loads(message)
        print(data['type'])
        if data['type']=="joinRoomRequest":#部屋参加リクエスト
            print(1)
        elif data['type']=="createRoomRequest":#部屋作成リクエスト
            print(uuid.uuid1())
        elif data['type']=="endCodePhaseRequest":#コーディング完了リクエスト
            print(3)
        elif data['type']=="endAnswerPhaseRequesta":#推測終了リクエスト
            print(4)
        elif data['type']=="openNextResultRequest":#開示リクエスト
            print(5)
        elif data['type']=="userIdRequest":#ユーザーIDリクエスト
            userIdResponse = {
                "type": "userIdResponse",
                "userId": data['userId'],
                "token": data['token'],
            }
            enc = json.dumps(userIdResponse,indent = 2)
            server.send_message_to_all(enc)
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
