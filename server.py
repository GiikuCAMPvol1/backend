import logging
import json
import uuid  # print(uuid.uuid1())
from collections import defaultdict

from websocket_server import WebsocketServer

# map<string,vector<strinng>>; roomIdに対して所属するメンバーのuseridを保持する。
room_member_id = defaultdict(list)

# map<string,vector<strinng>>; roomIdに対して所属するメンバーのusernameを保持する。
room_member_name = defaultdict(list)

# 部屋のIdを持つ配列 
room_name = []

# map<string,string> ;userid->username
name_id = {}

# map<string,bool> ;useiid->推測|コーディング終了したか。
id_bool = {}

# 発行した user_id と token を記録
user_token = dict()

# codeを記録する配列
ans_code = defaultdict(list)

# answerを記録する配列
ans_str = defaultdict(list)

# 問題
text = [
    "長さNの整数列A = (A1,A2,...AN)が与えられます。Aから偶数だけすべて取り出し、もとの順番を保って出力してください。",
    "英小文字からなる文字列Sが与えられます。Sの各文字を英大文字に変換して得られる文字列Tを出力してください。",
    "0と1の2種類の文字からなる文字列Sが与えられます。Sに含まれる0を1に、1を0に置き換えた文字列を出力してください。",
    "N個の文字列S1,S2,...SNがこの順番で与えられます。SN,SN-1,...S1の順番で出力してください。",
    "N個の整数A1,A2,...ANが与えられます。N個の整数を合計した値を求めてください。"
    "5つの整数A,B,C,D,Eが与えられます。この中に何種類の整数があるか出力してください。",
    "サッカーワールドカップは西暦年を4で割った余りが2である年の6月に行われます。現在がY年の1月であるとき、次のワールドカップはいつ開催されますか？（入力として整数Yが与えられます。）",
]


def join_room(req: dict):
    on_room_user_list_update = {
        "type": "onRoomUserListUpdate",
        "users": []
    }
    room_id = req['roomId']
    room_member_id[room_id].append(req['userId'])
    room_member_name[room_id].append(req['username'])
    on_room_user_list_update['users'].append(
        {
            "userId": room_member_id[room_id],
            "username": room_member_name[room_id]
        }
    )

    join_room_response = {
        "type": "joinRoomResponse",
        "roomId": room_id,
        "userId": req['userId'],
        "owner": False,
        "users": [
            {
                "userId": room_member_id[room_id],
                "username": room_member_name[room_id]
            }
        ]
    }
    return on_room_user_list_update, join_room_response


def create_room(req: dict) -> dict:
    res = {
        "type": "joinRoomResponse",
        "roomId": "<uuid>",
        "userId": "<uuid>",
        "owner": "<boolean>",
        "users": []
    }
    room_id = uuid.uuid4().hex
    room_member_id[room_id].append(req['userId'])
    room_member_name[room_id].append(req['username'])
    room_name.append(room_id)
    res['roomId'] = room_id
    res['userId'] = req['userId']
    res['owner'] = True
    res['users'].append(
        {
            "userId": room_member_id[room_id],
            "username": room_member_name[room_id]
        }
    )
    return res


def start_game(req: dict) -> dict:
    res = {
        "type": "onPhaseStart",
        "phase": "",
        "data": ""
    }
    room_id = req['roomId']
    siz = len(room_member_name)
    res['phase'] = "coding"
    res['data'] = text[3]
    return res


def end_phase(req: dict) -> dict:
    return


def open_next_result(req: dict) -> dict:
    return


def state_update(req: dict) -> dict:
    res = {
        "type": "onStateUpdate",
        "users": []
    }
    id1 = req['userId']
    res['users'].append(
        {
            "userId": req['userId'],
            "username": name_id[id1],
            "complated": True
        }
    )
    return res


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
        return

    def client_left(client: dict, server: WebsocketServer):
        print(f'ID={client["id"]} が切断されました')
        return

    def message_received(client: dict, server: WebsocketServer, message: str):
        print(f'ID={client["id"]} から "{message}" を受信しました')
        data = json.loads(message)
        print(data['type'])
        if data['type'] == "joinRoomRequest":  # 部屋参加リクエスト
            on_room_user_list_update, join_room_response = join_room(data)
            join_room_response_json = json.dumps(join_room_response, separators=(',', ':'))
            server.send_message(client, join_room_response_json)
            on_room_user_list_update_json = json.dumps(on_room_user_list_update, separators=(',', ':'))
            server.send_message_to_all(on_room_user_list_update_json)
        elif data['type'] == "createRoomRequest":  # 部屋作成リクエスト
            response = create_room(data)
            enc = json.dumps(response, separators=(',', ':'))
            server.send_message(client, enc)
        elif data['type'] == "endPhaseRequest":  # 状態終了リクエスト
            response = state_update(data)
            flag = True
            for S in id_bool:
                if S == False:
                    flag = True
            if flag == True:
                response2 = end_phase(data)
                enc2 = json.dumps(response2, separators=(',', ':'))
                server.send_message(client, enc2)
            enc = json.dumps(response, separators=(',', ':'))
            server.send_message(client, enc)
        elif data['type'] == "openNextResultRequest":  # 開示リクエスト
            response = open_next_result(data)
            enc = json.dumps(response, separators=(',', ':'))
            server.send_message(client, enc)
        elif data['type'] == "startGameRequest":  # ゲーム開始リクエスト
            response = start_game(data)
            enc = json.dumps(response, separators=(',', ':'))
            server.send_message(client, enc)
        elif data['type'] == "userIdRequest":  # ユーザーIDリクエスト
            response = request_user_id(data)
            enc = json.dumps(response, separators=(',', ':'))
            server.send_message(client, enc)
        elif data['type'] == "gameEndRequest":  # ゲーム終了リクエスト
            response = end_game(data)
            enc = json.dumps(response, separators=(',', ':'))
            server.send_message(client, enc)

    server = WebsocketServer(host='127.0.0.1', port=9001, loglevel=logging.DEBUG)
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    server.run_forever()
    return


if __name__ == '__main__':
    main()
