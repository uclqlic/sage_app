import os
import json
import base64
import streamlit as st
from rag_agent import RAGAgent

# ===== 页面配置 =====
st.set_page_config(
    page_title="Dao AI - Ancient Wisdom for Modern Times",
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== 加载 base64 图片 =====
def image_to_base64(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None

def get_avatar_base64(name: str):
    path = os.path.join("persona_protrait", f"{name}.png")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    fallback = os.path.join("persona_protrait", "bot_icon.png")
    if os.path.exists(fallback):
        with open(fallback, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    return None

def get_user_avatar():
    path = os.path.join("persona_protrait", "user_icon.png")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    return None

# ===== 现代化样式系统 =====
def apply_modern_styles():
    st.markdown("""
    <style>
    /* 导入现代字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;600&display=swap');
    
    /* 全局样式重置 */
    .stApp {
        font-family: 'Inter', 'Noto Sans SC', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #1a1a1a;
    }
    
    /* 隐藏默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* 侧边栏现代化设计 */
    .stSidebar {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(0, 0, 0, 0.06) !important;
    }
    
    .stSidebar > div:first-child {
        padding: 1.5rem !important;
    }
    
    /* 贤者选择卡片 */
    .sage-selector {
        margin-bottom: 1rem;
    }
    
    .sage-card {
        display: flex;
        align-items: center;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        background: rgba(248, 250, 252, 0.8);
        border: 1px solid rgba(226, 232, 240, 0.8);
        backdrop-filter: blur(8px);
    }
    
    .sage-card:hover {
        background: rgba(241, 245, 249, 0.9);
        border-color: #3b82f6;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
    }
    
    .sage-card.active {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        border-color: #1d4ed8;
        color: white;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4);
    }
    
    .sage-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 0.75rem;
        object-fit: cover;
        border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    .sage-card.active .sage-avatar {
        border-color: rgba(255, 255, 255, 0.6);
    }
    
    .sage-name {
        font-size: 0.875rem;
        font-weight: 500;
        flex: 1;
    }
    
    /* 主内容区域 */
    .main-content {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        margin: 1rem;
        padding: 2rem;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        min-height: calc(100vh - 2rem);
    }
    
    /* 品牌标题 */
    .brand-header {
        text-align: center;
        margin-bottom: 2rem;
        padding-bottom: 2rem;
        border-bottom: 1px solid rgba(226, 232, 240, 0.8);
    }
    
    .brand-logo {
        width: 80px;
        height: 80px;
        margin: 0 auto 1rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
    }
    
    .brand-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .brand-subtitle {
        font-size: 1rem;
        color: #64748b;
        font-weight: 400;
    }
    
    /* 当前对话状态 */
    .chat-status {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0.75rem 1.5rem;
        background: linear-gradient(135deg, #f8fafc, #e2e8f0);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 50px;
        margin: 1rem auto 2rem;
        max-width: 300px;
        font-size: 0.875rem;
        font-weight: 500;
        color: #475569;
    }
    
    .chat-status-icon {
        margin-right: 0.5rem;
        font-size: 1rem;
    }
    
    /* 聊天消息样式 */
    .stChatMessage {
        background: transparent !important;
        padding: 1rem 0 !important;
    }
    
    /* 输入框现代化 */
    .stChatInputContainer {
        background: rgba(248, 250, 252, 0.8) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(226, 232, 240, 0.8) !important;
        backdrop-filter: blur(8px) !important;
    }
    
    .stChatInputContainer:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-content {
            margin: 0.5rem;
            padding: 1rem;
            border-radius: 16px;
        }
        
        .brand-title {
            font-size: 2rem;
        }
        
        .sage-card {
            padding: 0.5rem;
        }
        
        .sage-avatar {
            width: 36px;
            height: 36px;
        }
    }
    
    /* 加载动画 */
    .stSpinner {
        text-align: center;
        color: #3b82f6;
    }
    
    /* 自定义滚动条 */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(226, 232, 240, 0.3);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(148, 163, 184, 0.5);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(148, 163, 184, 0.8);
    }
    </style>
    """, unsafe_allow_html=True)

# ===== 应用样式 =====
apply_modern_styles()

# ===== 加载人物 personas.json =====
@st.cache_data(show_spinner=False)
def load_personas():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, "personas.json"), "r", encoding="utf-8") as f:
        return json.load(f)

personas = load_personas()
mentor_names = list(personas.keys())

# ===== 初始化状态 =====
if "selected_mentor" not in st.session_state:
    st.session_state.selected_mentor = mentor_names[0]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent" not in st.session_state:
    st.session_state.agent = RAGAgent(persona=st.session_state.selected_mentor)

# ===== 左侧栏 - 现代化贤者选择器 =====
with st.sidebar:
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h3 style="font-size: 1.125rem; font-weight: 600; color: #1e293b; margin-bottom: 0.5rem;">
            Choose Your Sage
        </h3>
        <p style="font-size: 0.75rem; color: #64748b; margin: 0;">
            Select a philosopher to guide your journey
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 贤者选择卡片
    for mentor in mentor_names:
        mentor_avatar = get_avatar_base64(mentor)
        is_active = mentor == st.session_state.selected_mentor
        
        # 创建卡片HTML
        card_class = "sage-card active" if is_active else "sage-card"
        avatar_html = f'<img src="{mentor_avatar}" class="sage-avatar" alt="{mentor}">' if mentor_avatar else f'<div class="sage-avatar" style="background: linear-gradient(135deg, #667eea, #764ba2); display: flex; align-items: center; justify-content: center; color: white; font-weight: 600;">{mentor[0]}</div>'
        
        # 使用按钮进行选择
        if st.button(
            mentor,
            key=f"select_{mentor}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            if mentor != st.session_state.selected_mentor:
                st.session_state.selected_mentor = mentor
                st.session_state.agent = RAGAgent(persona=mentor)
                st.session_state.chat_history = []
                st.rerun()
        
        # 显示装饰性卡片
        st.markdown(f"""
        <div class="{card_class}" style="pointer-events: none; margin-top: -3rem; margin-bottom: 1rem;">
            {avatar_html}
            <div class="sage-name">{mentor}</div>
        </div>
        """, unsafe_allow_html=True)

# ===== 主内容区域 =====
with st.container():
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # 品牌标题
    st.markdown("""
    <div class="brand-header">
        <div class="brand-logo">🧘</div>
        <h1 class="brand-title">Dao AI</h1>
        <p class="brand-subtitle">Ancient Wisdom for Modern Times</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 当前对话状态
    st.markdown(f"""
    <div class="chat-status">
        <span class="chat-status-icon">💬</span>
        <span>Chatting with {st.session_state.selected_mentor}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 聊天历史
    for msg in st.session_state.chat_history:
        with st.chat_message("user", avatar=get_user_avatar()):
            st.markdown(msg["question"])
        with st.chat_message("assistant", avatar=get_avatar_base64(st.session_state.selected_mentor)):
            st.markdown(msg["answer"])
    
    # 输入框
    user_question = st.chat_input("Ask anything about life, wisdom, or philosophy...")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===== 处理用户输入 =====
if user_question:
    st.session_state.chat_history.append({"question": user_question, "answer": ""})
    st.rerun()

# ===== 生成答案 =====
if (
    st.session_state.chat_history and
    st.session_state.chat_history[-1]["answer"] == ""
):
    with st.spinner("🤔 The sage is contemplating..."):
        try:
            question = st.session_state.chat_history[-1]["question"]
            answer = st.session_state.agent.ask(question)
            st.session_state.chat_history[-1]["answer"] = answer
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.session_state.chat_history[-1]["answer"] = f"I apologize, but I encountered an error: {e}"
            st.rerun()
