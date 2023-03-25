import logging
import json
import uuid #print(uuid.uuid1())
from websocket_server import WebsocketServer

# 発行した user_id と token を記録
user_token = dict()

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

def request_user_id(req: dict) -> dict:
    res = {
        'type': 'userIdResponse'
    }
    # userId と token がリクエストに含まれている場合
    if ('userId' in req) and ('token' in req):
        user_id = req['userId']
        token = req['token']
        # サーバーが持っているデータと相違ないか検証
        if user_token.get(user_id, '') == token:
            # 提出された userId と token をレスポンスに乗せて返す
            res['userId'] = user_id
            res['token'] = token
            return res
    # userId と token を新規に発行する
    user_id = uuid.uuid4().hex
    token = uuid.uuid4().hex
    user_token[user_id] = token
    res['userId'] = user_id
    res['token'] = token
    return res

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
            response = request_user_id(data)
            # 読みやすいエンコード(デバッグ出力用)
            # _enc = json.dumps(response, indent=2)
            # print(_enc)
            # コンパクトなエンコード(通信用)
            enc = json.dumps(response, separators=(',', ':'))
            server.send_message(client, enc)
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
