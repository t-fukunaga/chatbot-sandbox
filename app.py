import os
import sys
import time
import json
import requests
import streamlit as st
from dotenv import load_dotenv

# .envがあれば環境変数を読込む
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

def get_response(api_key, conversation_id, query):
    url = os.environ.get("ENDPOINT")

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        "inputs": {},
        "query": query,
        # "response_mode": "streaming",
        "conversation_id": conversation_id,
        "user": "abc-123",
        "files": [
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    data = json.loads(response.text)
    print (data)
    return data['conversation_id'], data['answer']


def romeo_speaks(conversation_id, query):
    api_key = os.environ.get("ROMEO_API_KEY")
    return get_response(api_key, conversation_id, query)

def juliet_speaks(conversation_id, query):
    api_key = os.environ.get("JULIET_API_KEY")
    return get_response(api_key, conversation_id, query)


def main():
    st.title("ボット同士の会話")
    
    # アイコンのパス
    romeo_icon = "icon/romeo.png"
    juliet_icon = "icon/juliet.png"
    user_icon = "icon/user.png"

    # チャット履歴と会話ID、juliet_resultの初期化
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.con_id1 = ""
        st.session_state.con_id2 = ""
        st.session_state.juliet_result = ""
        st.session_state.user_input = ""  # ユーザー入力の初期化
        st.session_state.input_displayed = True  # 入力表示の状態を管理

    # チャット画面の表示
    for message in st.session_state.chat_history:
        cols = st.columns([1, 5])  # 1:5 の比率で列を作成
        if message["is_user"]:
            cols[0].image(user_icon, width=60)
            cols[1].write("あなた: " + message["text"])
        elif message["bot"] == "romeo":
            cols[0].image(romeo_icon, width=60)
            cols[1].write("" + message["text"])
        elif message["bot"] == "juliet":
            cols[0].image(juliet_icon, width=60)
            cols[1].write("" + message["text"])
    
    # ユーザーの入力を取得
    if st.session_state.input_displayed:
        user_input = st.text_input("ロミオの最初の台詞を入れてください", value=st.session_state.user_input)
        button_label = "送信"
    else:
        user_input = None
        button_label = "続ける"
    
    # ボタンを押したときの処理
    if st.button(button_label):
        if user_input:
            st.session_state.user_input = user_input  # 入力をセッション状態に保存
            # ロミオが応答
            st.session_state.con_id1, result = romeo_speaks(st.session_state.con_id1, f"ジュリエットに対して、あなたから会話を開始します。最初の会話は以下の文章で始めてください。\n\n{user_input}")
            st.session_state.chat_history.append({"is_user": False, "text": result, "bot": "romeo"})

            # ジュリエットが応答
            st.session_state.con_id2, result = juliet_speaks(st.session_state.con_id2, result)
            st.session_state.chat_history.append({"is_user": False, "text": result, "bot": "juliet"})
            st.session_state.juliet_result = result
        else:
            # ロミオが応答
            st.session_state.con_id1, result = romeo_speaks(st.session_state.con_id1, st.session_state.juliet_result)
            st.session_state.chat_history.append({"is_user": False, "text": result, "bot": "romeo"})

            # ジュリエットが応答
            st.session_state.con_id2, result = juliet_speaks(st.session_state.con_id2, result)
            st.session_state.chat_history.append({"is_user": False, "text": result, "bot": "juliet"})
            st.session_state.juliet_result = result

        st.session_state.user_input = ""  # 入力をクリア
        st.session_state.input_displayed = False  # 入力フォームを非表示に設定
        st.experimental_rerun()  # 画面を更新

if __name__ == "__main__":
    main()