import logging
import json
import uuid #print(uuid.uuid1())
from collections import defaultdict

from websocket_server import WebsocketServer

#map<string,vector<strinng>>; roomIdに対して所属するメンバーのuseridを保持する。
room_member_id = defaultdict(list)

#map<string,vector<strinng>>; roomIdに対して所属するメンバーのusernameを保持する。
room_member_name = defaultdict(list)

#部屋のIdを持つ配列 
room_name = [] 

#map<string,string> ;userid->username
name_id = {}



# 発行した user_id と token を記録
user_token = dict()

def join_room(req: dict) -> dict:
    res = {
        "type": "onRoomUserListUpdate",
        "users": []
    }
    room_Id = req['roomId']
    room_member_id[room_Id].append(req['userId'])
    room_member_name[room_Id].append(req['username'])
    res['users'].append(
        {
            "userId": room_member_id[room_Id],
            "username": room_member_name[room_Id]
        }
    )
    return res

def create_room(req: dict) -> dict:
    res = {
        "type": "joinRoomResponse",
        "roomId": "<uuid>",
        "userId": "<uuid>",
        "owner": "<boolean>",
        "users": []
    }
    room_Id = uuid.uuid4().hex
    room_member_id[room_Id].append(req['userId'])
    room_member_name[room_Id].append(req['username'])
    room_name.append(room_Id)
    res['roomId'] = room_Id
    res['userId'] = req['userId']
    res['owner'] = True
    res['users'].append(
        {
            "userId": room_member_id[room_Id],
            "username": room_member_name[room_Id]
        }
    )
    return res

def start_game(req: dict) -> dict:
    res = {
        "type": "onPhaseStart",
        "phase": "",
        "data": "<string>"
    }
    return res

def end_phase(req: dict) -> dict:
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


def end_game(req: dict) -> dict:
    res = {
        "type": "onGameEnd"
    }
    return res

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
            response = join_room(data)
            enc = json.dumps(response, separators=(',',':'))
            server.send_message(client, enc)
        elif data['type']=="createRoomRequest":#部屋作成リクエスト
            response = create_room(data)
            enc = json.dumps(response, separators=(',',':'))
            server.send_message(client, enc)
        elif data['type']=="endPhaseRequest":#終了リクエスト
            response = end_phase(data)
            enc = json.dumps(response, separators=(',',':'))
            server.send_message(client, enc)
        elif data['type']=="openNextResultRequest":#開示リクエスト
            response = open_next_result(data)
            enc = json.dumps(response, separators=(',',':'))
            server.send_message(client, enc)
        elif data['type']=="startGameRequest":#ゲーム開始リクエスト
            response = start_game(data)
            enc = json.dumps(response, separators=(',',':'))
            server.send_message(client, enc)
        elif data['type']=="userIdRequest":#ユーザーIDリクエスト
            response = request_user_id(data)
            enc = json.dumps(response, separators=(',', ':'))
            server.send_message(client, enc)
        elif data['type']=="gameEndRequest":#ゲーム終了リクエスト
            response = end_game(data)
            enc = json.dumps(response, separators=(',',':'))
            server.send_message(client, enc)

    server = WebsocketServer(host='127.0.0.1', port=9001, loglevel=logging.DEBUG)
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    server.run_forever()
    return

if __name__ == '__main__':
    main()
