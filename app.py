import streamlit as st
from google_play_scraper import app
import requests
from io import BytesIO
import zipfile

# 页面配置
st.set_page_config(page_title="Google Play 多国商店图抓取工具", layout="wide")

st.title("🌐 Google Play 全球商店图抓取助手")
st.markdown("输入 APP 链接，选择国家，一键预览并打包下载本地化素材。")

# --- 侧边栏配置 ---
st.sidebar.header("配置参数")
app_url = st.sidebar.text_input("1. 粘贴 Google Play 链接",
                                value="https://play.google.com/store/apps/details?id=com.tencent.ig")


# 提取包名
def extract_package_id(url):
    if "id=" in url:
        return url.split("id=")[1].split("&")[0]
    return url


package_id = extract_package_id(app_url)

# 国家选项（常用国家）
country_options = {
    "美国 (US)": "us", "日本 (JP)": "jp", "韩国 (KR)": "kr",
    "英国 (GB)": "gb", "德国 (DE)": "de", "法国 (FR)": "fr",
    "巴西 (BR)": "br", "印度 (IN)": "in", "泰国 (TH)": "th",
    "新加坡 (SG)": "sg", "越南 (VN)": "vn", "沙特 (SA)": "sa"
}

selected_countries = st.sidebar.multiselect(
    "2. 选择要爬取的国家",
    options=list(country_options.keys()),
    default=["美国 (US)", "日本 (JP)"]
)

fetch_button = st.sidebar.button("🚀 开始抓取")

# --- 主界面逻辑 ---
if fetch_button:
    if not package_id:
        st.error("请输入有效的 APP 链接或包名")
    else:
        for country_label in selected_countries:
            gl_code = country_options[country_label]

            with st.spinner(f"正在获取 {country_label} 的素材..."):
                try:
                    # 获取数据
                    details = app(package_id, lang='en', country=gl_code)
                    screenshots = details.get('screenshots', [])

                    if not screenshots:
                        st.warning(f"{country_label} 没有找到截图。")
                        continue

                    # 界面展示：每一行一个国家
                    st.subheader(f"📍 国家/地区: {country_label}")

                    # 准备 ZIP 下载
                    buf = BytesIO()
                    with zipfile.ZipFile(buf, "w") as zf:
                        # 展示图片列
                        cols = st.columns(5)  # 每行显示5张预览
                        for idx, url in enumerate(screenshots):
                            # 显示预览
                            cols[idx % 5].image(url, use_container_width=True)

                            # 将图片加入 ZIP 压缩包
                            img_res = requests.get(url)
                            zf.writestr(f"{gl_code}_screenshot_{idx + 1}.png", img_res.content)

                    # 下载按钮（放在该国家的标题旁边）
                    st.download_button(
                        label=f"📂 一键下载 {country_label} 截图包",
                        data=buf.getvalue(),
                        file_name=f"{package_id}_{gl_code}.zip",
                        mime="application/zip",
                        key=f"btn_{gl_code}"
                    )
                    st.divider()  # 分割线

                except Exception as e:
                    st.error(f"处理 {country_label} 时出错: {str(e)}")

# 初始化提示
if not fetch_button:
    st.info("请在左侧填入信息并点击【开始抓取】")