import streamlit as st
import requests
import pandas as pd
from config import PAGE_CONFIG

st.set_page_config(**PAGE_CONFIG)
st.title("📊 Drowsiness Monitoring Dashboard")

# Gọi API lấy dữ liệu log
response = requests.get("http://127.0.0.1:8000/api/logs")

if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data)

    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        st.subheader("📋 Log dữ liệu")
        st.dataframe(df)

        st.subheader("📈 Biểu đồ buồn ngủ")
        st.line_chart(df.set_index("timestamp")["drowsy_score"])

        st.subheader("🔔 Thiết bị cảnh báo gần nhất")
        last = df.iloc[-1]
        st.write(f"**Driver ID**: {last['driver_id']}")
        st.write(f"**Score**: {last['drowsy_score']}")
        st.write(f"**LED**: {last['led']} | **Buzzer**: {last['buzzer']}")
        st.write(f"**Time**: {last['timestamp']}")
    else:
        st.warning("Chưa có dữ liệu.")
else:
    st.error("Không thể lấy dữ liệu từ server.")
