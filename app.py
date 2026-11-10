import json
import os
import openai
import streamlit as st

# Cấu hình kết nối Poe API
api_key = (
    st.secrets["POE_API_KEY"]
    if "POE_API_KEY" in st.secrets
    else os.getenv("POE_API_KEY")
)
client = openai.OpenAI(api_key=api_key, base_url="https://api.poe.com/v1")

st.title("🤖 Chatbot Tư Vấn Hướng Nghiệp & Việc Làm Quảng Ngãi")


# Đọc dữ liệu từ file jobs_quangngai.json nếu có
@st.cache_data
def load_job_data():
  if os.path.exists("jobs_quangngai.json"):
    with open("jobs_quangngai.json", "r", encoding="utf-8") as f:
      return f.read()
  return ""


job_data_str = load_job_data()

# Khởi tạo lịch sử chat kèm theo ngữ cảnh dữ liệu việc làm Quảng Ngãi
if "messages" not in st.session_state:
  st.session_state.messages = [{
      "role": "system",
      "content": (
          "Bạn là một trợ lý AI thông minh chuyên tư vấn hướng nghiệp và việc"
          " làm tại tỉnh Quảng Ngãi. Hãy dựa vào dữ liệu việc làm thực tế sau"
          f" để trả lời người dùng một cách chính xác:\n{job_data_str}"
      ),
  }]

# Hiển thị lịch sử tin nhắn trên giao diện
for message in st.session_state.messages:
  if message["role"] != "system":
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

# Nhập câu hỏi từ người dùng
if prompt := st.chat_input(
    "Bạn muốn tìm việc làm hoặc tư vấn ngành nghề nào ở Quảng Ngãi?"
):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  # Gọi API từ Poe
  with st.chat_message("assistant"):
    with st.spinner("Đang tìm kiếm thông tin..."):
      try:
        response = client.chat.completions.create(
            model="GPT-4o-mini",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
        )
        reply = response.choices[0].message.content
        st.markdown(reply)
        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )
      except Exception as e:
        st.error(f"Đã xảy ra lỗi kết nối: {e}")