import json
import os
import google.generativeai as genai
import streamlit as st

st.set_page_config(
    page_title="Chatbot Tư Vấn Hướng Nghiệp Quảng Ngãi", page_icon="🤖"
)

# Thay thế "DANG_KY_API_KEY_CUA_BAN_O_DAY" bằng API Key thật của bạn
GOOGLE_API_KEY = "AQ.Ab8RN6K18OblOrWhCE5xsVkvJcYxsP1hPUAW8Ht-fpr8_R5uOw"

if GOOGLE_API_KEY == "DANG_KY_API_KEY_CUA_BAN_O_DAY":
    st.error("⚠️ Bạn chưa điền Google API Key trong file app.py!")
else:
    genai.configure(api_key=GOOGLE_API_KEY)


@st.cache_data
def load_job_data():
  if os.path.exists("jobs_quangngai.json"):
    with open("jobs_quangngai.json", "r", encoding="utf-8") as f:
      return json.load(f)
  return []


job_database = load_job_data()

st.title("🤖 Chatbot Tư Vấn Hướng Nghiệp & Việc Làm Quảng Ngãi")
st.markdown(
    "Ứng dụng hỗ trợ phân tích sở thích, định hướng học tập và việc làm thực tế"
    " tại địa phương."
)

try:
  model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
  st.error(f"Lỗi khởi tạo AI: {e}")

if "messages" not in st.session_state:
  st.session_state.messages = [{
      "role": "model",
      "parts": [
          "Xin chào! Hãy chia sẻ sở thích, chuyên ngành học và mong muốn công"
          " việc của bạn tại Quảng Ngãi để tôi tư vấn nhé."
      ],
  }]

for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["parts"][0])

if user_input := st.chat_input("Nhập sở thích hoặc câu hỏi của bạn..."):
  st.session_state.messages.append({"role": "user", "parts": [user_input]})
  with st.chat_message("user"):
    st.markdown(user_input)

  system_instruction = f"""
    Bạn là chuyên gia tư vấn hướng nghiệp tại Quảng Ngãi. Hãy tư vấn cho người dùng dựa trên:
    - Sở thích, học tập và định hướng cá nhân của họ.
    - Thị trường lao động thực tế tại Quảng Ngãi (KKT Dung Quất, KCN VSIP, TP. Quảng Ngãi).
    
    Dữ liệu việc làm tham khảo:
    {json.dumps(job_database, ensure_ascii=False, indent=2)}
    """

  chat_history_for_gemini = []
  for msg in st.session_state.messages:
    gemini_role = "user" if msg["role"] == "user" else "model"
    chat_history_for_gemini.append(
        {"role": gemini_role, "parts": msg["parts"]}
    )

  try:
    with st.spinner("Đang tìm kiếm cơ hội và phân tích..."):
      chat_session = model.start_chat(history=chat_history_for_gemini[:-1])
      response = chat_session.send_message(
          f"{system_instruction}\n\nYêu cầu của người dùng: {user_input}"
      )
      bot_reply = response.text

    with st.chat_message("model"):
      st.markdown(bot_reply)

    st.session_state.messages.append({"role": "model", "parts": [bot_reply]})
  except Exception as e:
    st.error(f"Lỗi kết nối AI: {e}")