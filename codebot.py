import streamlit as st
import requests
import json
import time
import os

model = "codegemma:7b"

def format_response(msg_content):
    lines = msg_content.split('\n')
    for line in lines:
        indentation = len(line) - len(line.lstrip())
        words = line.split()

        yield " " * indentation

        for word in words:
            yield word + " "
            time.sleep(0.1)

        yield "\n"

def chat(messages):
    try:
        with requests.post(
            "http://localhost:11434/api/chat",
            json={"model": model, "messages": messages, "stream": True},
            stream=True
        ) as response:
            response.raise_for_status()
            
            output = []
            for line in response.iter_lines():
                if line:
                    body = json.loads(line)
                    
                    if "error" in body:
                        raise Exception(body["error"])

                    if body.get("done", False):
                        return {"role": "assistant", "content": ''.join(output)}

                    output.append(body.get("message", {}).get("content", ""))
    except requests.RequestException as e:
        return {"role": "assistant", "content": f"Request error: {e}"}
    except Exception as e:
        return {"role": "assistant", "content": str(e)}

def main():
    st.title("Codebot")
    st.subheader("By the developers, For the developers")
    user_input = st.chat_input("Enter your prompt:", key="1")

    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    if user_input:
        with st.chat_message("user",):
                st.write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        with_history = "\\n".join(msg["content"] for msg in st.session_state.messages if msg["role"] == "user")
        messages = [
            {"role": "system", "content": "You are helpful coding assistant with capability to optimise the code for performance."},
            {"role": "user", "content": with_history}
        ]

        response = chat(messages)
        st.session_state.messages.append(response)
        with st.chat_message("assistant"):
            st.write_stream(format_response(response["content"]))

    elif st.session_state['messages'] is None:
        st.info("Enter a prompt")


if __name__ == "__main__":
    main()