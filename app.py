import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import io

# ==========================
# Cấu hình trang
# ==========================
st.set_page_config(page_title="Phân Tích Điểm Bất Thường", layout="wide", page_icon="📊")

# Hotlink Imgur cho hình ảnh (ví dụ, bạn cần thay thế bằng URL thực tế của mình)
# RẤT QUAN TRỌNG: THAY THẾ URL NÀY BẰNG HÌNH ẢNH THỰC TẾ CỦA BẠN
IMGUR_IMAGE_URL = "https://i.imgur.com/your_image_link.png"

# CSS tùy chỉnh
st.markdown(f"""
<style>
    .main {{ background-color: #f0f2f6; }}
    .stButton>button {{ background-color: #4CAF50; color: white; border-radius: 5px; }}
    .stFileUploader>label {{ font-weight: bold; }}
    .css-1d391kg {{ background-color: #ffffff; border-radius: 10px; padding: 20px; }}
    h1 {{ color: #2c3e50; }}
    h2 {{ color: #34495e; }}
    .stAlert {{ border-radius: 5px; }}
    footer {{ visibility: hidden; }}
    .footer {{
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #2c3e50;
        color: white;
        text-align: center;
        padding: 10px;
    }}

    /* === TÙY CHỈNH SLIDER Z-SCORE === */
    /* Nhắm mục tiêu cụ thể vào slider trong sidebar (Ngưỡng Z-Score) */
    
    /* 1. Thanh trượt chung (Track) */
    [data-testid="stSidebarContent"] .stSlider > div > div:nth-child(2) > div {{
        background: #ccc; /* Màu nền thanh trượt */
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.5); /* Hiệu ứng lõm (3D-like) */
        border-radius: 5px;
    }}
    
    /* 2. Phần đã chọn (Fill) */
    [data-testid="stSidebarContent"] .stSlider > div > div:nth-child(2) > div > div[data-testid="stTrackFill"] {{
        background: #4CAF50; /* Màu fill */
        box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.3); /* Hiệu ứng nổi (3D-like) */
        border-radius: 5px;
    }}

    /* 3. Núm kéo (Thumb) và Cursor */
    [data-testid="stSidebarContent"] [data-testid="stThumbValue"] {{
        background: #FF5722; /* Màu núm */
        border: 3px solid #E64A19; /* Viền */
        width: 25px !important; /* Tăng kích thước núm */
        height: 25px !important; 
        border-radius: 50%; /* Hình tròn */
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.4), 0 6px 20px 0 rgba(0,0,0,0.3); /* Hiệu ứng nổi 3D */
        cursor: grab !important; /* THAY ĐỔI CURSOR */
        transform: scale(1.1); /* Hơi to hơn */
    }}
    
    /* 4. Hiệu ứng khi kéo (Active state) */
    [data-testid="stSidebarContent"] [data-testid="stThumbValue"]:active {{
        cursor: grabbing !important;
        transform: scale(1.3); /* To hơn khi kéo */
        box-shadow: 0 5px 15px rgba(0,0,0,0.5);
    }}

    /* Tùy chỉnh tiêu đề và upload file để dùng cột */
    .file-uploader-container {{
        display: flex;
        flex-direction: row;
        gap: 20px; /* Khoảng cách giữa các cột */
    }}
</style>
""", unsafe_allow_html=True)

# ==========================
# Header logo
# ==========================
col_logo, col_title = st.columns([1,6])
with col_logo:
    try:
        st.image("Logo_Marie_Curie.png", width=100)
    except:
        st.write("🏫 THPT Marie Curie")
with col_title:
    st.title("📊 Phân Tích Điểm Số Bất Thường Sử Dụng Z-Score")

st.markdown("""
Ứng dụng phân tích điểm số bất thường dựa trên Z-score. 
- File CSV cần có header: "MaHS", "Lop", các cột môn học. 
- Z-score: Điểm bất thường nếu |z-score| > ngưỡng (mặc định 2). 
- Hỗ trợ UTF-8.
""")

# ==========================
# Sidebar
# ==========================
with st.sidebar:
    st.header("🛠 Cài đặt")
    z_threshold = st.slider("Ngưỡng Z-Score", 1.0, 5.0, 2.0, 0.1)
    st.markdown("---")
    st.info("CSV phải có cột số cho điểm và mã hóa UTF-8.")

# ==========================
# Upload file và Hiển thị hình ảnh
# ==========================

# Chia cột cho khu vực Upload và Hình ảnh
col_upload, col_image = st.columns([1, 1])

with col_upload:
    uploaded_file = st.file_uploader("📂 Upload bảng điểm (CSV)", type="csv")

with col_image:
    # Hiển thị hình ảnh từ hotlink Imgur
    st.image(IMGUR_IMAGE_URL, width=540, caption="Hình ảnh minh họa dữ liệu (1080x560)")

if uploaded_file is not None:
    # Đọc file CSV
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding='latin1')
        st.warning("File không phải UTF-8, đã dùng latin1.")

    # Chuẩn hóa tên cột
    df.columns = df.columns.str.strip().str.replace(' ','').str.capitalize()

    # Kiểm tra cột lớp
    class_col = [c for c in df.columns if c.lower()=='lop']
    if not class_col:
        st.error("Không tìm thấy cột 'Lop'.")
        st.stop()
    df['Lop'] = df[class_col[0]]

    # Kiểm tra cột học sinh
    student_col = [c for c in df.columns if c.lower() in ['mahs','id','studentid']]
    if not student_col:
        st.error("Không tìm thấy cột 'MaHS'.")
        st.stop()
    df['MaHS'] = df[student_col[0]]

    # Chọn các cột môn học
    subject_cols = [c for c in df.columns if c not in ['MaHS','Lop']]
    if len(subject_cols)==0:
        st.error("Không tìm thấy cột điểm môn học.")
        st.stop()

    # Multi chọn lớp + môn
    classes = st.multiselect("Chọn lớp để lọc", sorted(df['Lop'].unique()), default=sorted(df['Lop'].unique()))
    subjects = st.multiselect("Chọn môn để phân tích", subject_cols, default=subject_cols)

    df_filtered = df[df['Lop'].isin(classes)].copy()
    if df_filtered.empty:
        st.warning("Không có dữ liệu cho lớp được chọn.")
        st.stop()

    # Tính Z-score riêng từng môn
    for subj in subjects:
        df_filtered[f'Z_{subj}'] = stats.zscore(df_filtered[subj].fillna(0))
        df_filtered[f'Highlight_{subj}'] = df_filtered[f'Z_{subj}'].abs() > z_threshold

    # ==========================
    # Bảng dữ liệu
    # ==========================
    st.subheader("📋 Bảng điểm gốc và bất thường")
    col1, col2 = st.columns([3,1])

    with col1:
        st.write("**Bảng gốc học sinh**")
        st.dataframe(df_filtered[['MaHS','Lop']+subjects], use_container_width=True)

        # Tạo bảng bất thường
        anomaly_cols = ['MaHS','Lop'] + [subj for subj in subjects]
        anomalies = df_filtered.copy()
        # giữ lại học sinh bất thường bất kỳ môn
        anomalies = anomalies[anomalies[[f'Highlight_{subj}' for subj in subjects]].any(axis=1)]
        st.write("**Học sinh bất thường**")
        st.dataframe(anomalies[anomaly_cols], use_container_width=True)

        # Download CSV
        csv_buffer = io.StringIO()
        anomalies.to_csv(csv_buffer, index=False, encoding='utf-8')
        st.download_button("📥 Xuất CSV học sinh bất thường", csv_buffer.getvalue(), file_name="Students_Anomalies.csv")

    # ==========================
    # Biểu đồ cột tổng học sinh vs học sinh bất thường theo lớp
    # ==========================
    st.subheader("📊 Biểu đồ cột theo lớp")
    class_summary = df_filtered.groupby('Lop').size().reset_index(name='Tổng học sinh')
    anomaly_count = anomalies.groupby('Lop').size().reset_index(name='Học sinh bất thường')
    summary = pd.merge(class_summary, anomaly_count, on='Lop', how='left').fillna(0)

    fig_col = px.bar(summary, x='Lop', y=['Tổng học sinh','Học sinh bất thường'],
                      barmode='group', color_discrete_map={'Tổng học sinh':'#4CAF50','Học sinh bất thường':'#FF5252'},
                      labels={'value':'Số học sinh','Lop':'Lớp'}, title="Tổng học sinh & Học sinh bất thường theo lớp")
    st.plotly_chart(fig_col, use_container_width=True)

    # ==========================
    # Scatter & Histogram từng môn
    # ==========================
    st.subheader("📈 Scatter & Histogram theo môn")
    for subj in subjects:
        st.markdown(f"### {subj}")

        # Scatter
        fig_scat = px.scatter(df_filtered, x='MaHS', y=subj, color=f'Z_{subj}',
                              color_continuous_scale='RdYlGn_r', 
                              size=df_filtered[f'Z_{subj}'].abs(),
                              size_max=20,
                              hover_data={'MaHS':True, subj:True, f'Z_{subj}':True})
        st.plotly_chart(fig_scat, use_container_width=True)

        # Histogram
        fig_hist = px.histogram(df_filtered, x=subj, nbins=20, color=f'Highlight_{subj}',
                                 color_discrete_map={True:'#FF0000', False:'#4CAF50'},
                                 labels={'count':'Số học sinh'})
        st.plotly_chart(fig_hist, use_container_width=True)

# ==========================
# Footer
# ==========================
st.markdown("""
<div class="footer">
    <p><b>Nhóm Thực Hiện:</b> Lại Nguyễn Minh Trí và những người bạn</p>
    <p>📞 Liên hệ: 0908-083566 | 📧 Email: laingminhtri@gmail.com</p>
    <p>© 2025 Trường THPT Marie Curie - Dự án Phân Tích Điểm Bất Thường</p>
</div>
""", unsafe_allow_html=True)
