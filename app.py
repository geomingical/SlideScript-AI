"""
演講逐字稿生成器 - Streamlit 版本
使用 GPT-5.1/o3/GPT-4o 等模型，將投影片 PDF 轉換為專業演講逐字稿
"""

import os
import base64
import streamlit as st
from datetime import datetime
from typing import List, Dict, Optional
import fitz  # PyMuPDF
from pydub import AudioSegment
from openai import OpenAI


class PDFProcessor:
    """處理 PDF 投影片的類別"""
    
    def __init__(self):
        self.slides_content = []
    
    def extract_slides(self, pdf_file) -> List[Dict[str, str]]:
        """從 PDF 提取每一頁的內容"""
        try:
            # 儲存上傳的 PDF
            pdf_path = "/tmp/presentation.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(pdf_file.read())
            
            doc = fitz.open(pdf_path)
            
            if len(doc) == 0:
                doc.close()
                raise Exception("此 PDF 檔案不包含任何頁面")
            
            slides = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text().strip()
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_data = pix.tobytes("png")
                
                slides.append({
                    "page": page_num + 1,
                    "text": text if text else "[此頁無文字內容]",
                    "image": base64.b64encode(img_data).decode()
                })
            
            doc.close()
            self.slides_content = slides
            return slides
            
        except Exception as e:
            raise Exception(f"PDF 處理錯誤: {str(e)}")


class AudioAnalyzer:
    """使用 GPT-4o Audio API 分析音頻並計算語速"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.words_per_minute = None
    
    def _convert_to_mp3(self, audio_path: str) -> str:
        """將音頻轉換為 mp3 格式"""
        try:
            audio = AudioSegment.from_file(audio_path)
            mp3_path = "/tmp/converted_audio.mp3"
            audio.export(mp3_path, format="mp3", bitrate="128k")
            return mp3_path
        except Exception as e:
            raise Exception(f"音頻格式轉換錯誤: {str(e)}")
    
    def analyze_audio(self, audio_file) -> float:
        """使用 GPT-4o Audio API 分析音頻並計算語速"""
        try:
            # 儲存上傳的音頻
            audio_path = "/tmp/audio_sample.m4a"
            with open(audio_path, 'wb') as f:
                f.write(audio_file.read())
            
            audio = AudioSegment.from_file(audio_path)
            duration_seconds = len(audio) / 1000.0
            
            if duration_seconds < 5:
                raise Exception("音頻時長過短（少於 5 秒），建議上傳 20 秒左右的音頻")
            if duration_seconds > 120:
                raise Exception("音頻時長過長（超過 2 分鐘），請上傳 20-60 秒的音頻樣本")
            
            # 轉換為 mp3
            mp3_path = self._convert_to_mp3(audio_path)
            
            # 使用 GPT-4o Audio API 進行轉錄
            with open(mp3_path, 'rb') as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="zh"
                )
            
            text = transcription.text
            
            if not text or len(text.strip()) == 0:
                raise Exception("無法識別音頻內容，請確保音頻清晰且包含語音")
            
            # 計算字數
            char_count = len([c for c in text if c.strip() and not c.isspace()])
            wpm = (char_count / duration_seconds) * 60
            self.words_per_minute = wpm
            
            # 清理暫存檔
            if os.path.exists(audio_path):
                os.remove(audio_path)
            if os.path.exists(mp3_path):
                os.remove(mp3_path)
            
            return wpm
            
        except Exception as e:
            raise Exception(f"音頻分析錯誤: {str(e)}")


class TranscriptGenerator:
    """使用 OpenAI Vision 模型生成演講逐字稿"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.transcript = ""
    
    def generate_transcript(
        self,
        slides: List[Dict[str, str]],
        target_duration: int,
        words_per_minute: float,
        style: str,
        topic: str,
        audience: str,
        language: str,
        model_name: str = "gpt-5.1",
        expert_role: Optional[str] = None,
        include_tips: bool = False
    ) -> str:
        """生成演講逐字稿"""
        try:
            if not slides or len(slides) == 0:
                raise Exception("沒有投影片內容，請先上傳 PDF 檔案")
            
            target_words = int(target_duration * words_per_minute)
            words_per_slide = target_words // len(slides)
            
            system_prompt = self._create_system_prompt(
                style, topic, audience, language, expert_role, words_per_slide, include_tips
            )
            
            tips_instruction = ""
            if include_tips:
                tips_instruction = """

【演講技巧建議】
請在逐字稿中適當位置加入以下演講技巧建議（使用 [方括號] 標註）：
- [手勢：展開雙手] - 在強調重點時
- [手勢：指向投影片] - 在說明圖表時
- [語氣：提高音量] - 在關鍵訊息時
- [語氣：放慢速度] - 在重要概念時
- [暫停 2-3 秒] - 在段落轉換時
- [眼神接觸] - 在與聽眾互動時
- [走動：移向舞台中央] - 在開場或總結時
"""
            
            user_content = [
                {
                    "type": "text",
                    "text": f"""
請根據以下投影片圖片，生成一份完整的演講逐字稿。

演講參數：
- 總時長：{target_duration} 分鐘
- 語速：每分鐘約 {int(words_per_minute)} 字
- 目標總字數：約 {target_words} 字
- 每頁建議字數：約 {words_per_slide} 字
- 輸出語言：{language}{tips_instruction}

輸出格式要求：
Slide 1
[第一頁的演講內容]

Slide 2
[第二頁的演講內容]

...以此類推

請確保：
1. 仔細觀察每頁投影片的視覺元素、圖表、文字
2. 每頁的逐字稿自然流暢，講解投影片上的重點
3. 內容銜接順暢，有開場和結尾
4. 符合指定的演講風格和語氣
5. 總字數控制在 {target_words} 字左右（可上下浮動10%）
"""
                }
            ]
            
            # 添加所有投影片圖片
            for slide in slides:
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{slide['image']}",
                        "detail": "high"
                    }
                })
            
            # 呼叫 OpenAI Vision API
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.7,
                max_completion_tokens=4000
            )
            
            transcript = response.choices[0].message.content
            self.transcript = transcript
            
            return transcript
            
        except Exception as e:
            error_msg = str(e)
            if "API key" in error_msg or "authentication" in error_msg.lower():
                raise Exception("❌ API Key 錯誤，請確認您的 OpenAI API Key 是否正確")
            elif "rate limit" in error_msg.lower():
                raise Exception("❌ API 請求過於頻繁，請稍後再試")
            elif "quota" in error_msg.lower():
                raise Exception("❌ API 額度不足，請檢查您的 OpenAI 帳戶餘額")
            else:
                raise Exception(f"逐字稿生成錯誤: {error_msg}")
    
    def _create_system_prompt(
        self,
        style: str,
        topic: str,
        audience: str,
        language: str,
        expert_role: Optional[str],
        words_per_slide: int,
        include_tips: bool = False
    ) -> str:
        """建立系統提示"""
        
        style_descriptions = {
            "活潑": "使用輕鬆、活潑的語氣，適度加入互動和幽默元素",
            "嚴肅": "使用正式、專業的語氣，保持學術嚴謹性",
            "激勵": "使用鼓舞人心的語言，充滿正能量和動力",
            "教學": "使用清晰、易懂的解釋方式，像是在教導學生",
            "對話": "使用對話式的語氣，如同與聽眾面對面交談"
        }
        
        language_instructions = {
            "繁體中文": "使用繁體中文輸出",
            "英文": "使用英文輸出",
            "簡體中文": "使用簡體中文輸出",
            "日文": "使用日文輸出",
            "韓文": "使用韓文輸出",
            "西班牙文": "使用西班牙文輸出",
            "法文": "使用法文輸出",
            "德文": "使用德文輸出"
        }
        
        role_intro = ""
        if expert_role:
            role_intro = f"你是一位{expert_role}，"
        
        style_desc = style_descriptions.get(style, "使用自然流暢的語氣")
        lang_inst = language_instructions.get(language, "使用繁體中文輸出")
        
        tips_requirement = ""
        if include_tips:
            tips_requirement = """
7. 在適當位置加入演講技巧建議，使用 [方括號] 標註，包括：
   - 手勢建議（如：展開雙手、指向投影片、握拳強調）
   - 語氣建議（如：提高音量、放慢速度、加重語氣）
   - 暫停時機（如：[暫停 2-3 秒]）
   - 肢體語言（如：眼神接觸、走動、身體前傾）
   這些建議應自然融入逐字稿中，幫助演講者更好地傳達訊息
"""
        
        return f"""
{role_intro}你是一位經驗豐富的演講者和內容創作專家。

演講主題：{topic}
目標聽眾：{audience}
演講風格：{style_desc}
語言要求：{lang_inst}

你的任務是根據提供的投影片內容，創作一份自然、流暢、引人入勝的演講逐字稿。

要求：
1. 內容必須忠於投影片，但要用口語化的方式表達
2. 每頁約 {words_per_slide} 字，可根據內容重要性調整
3. 開場要吸引人，結尾要有力
4. 適時加入過渡語，讓內容銜接流暢
5. 符合指定的演講風格和目標聽眾
6. 確保內容專業準確，同時易於理解{tips_requirement}
"""


# Streamlit 主應用程式
def main():
    st.set_page_config(
        page_title="演講逐字稿生成器",
        page_icon="🎤",
        layout="wide"
    )
    
    # 自定義 CSS
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 0.5rem 2rem;
        border-radius: 8px;
        border: none;
    }
    .info-box {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 標題
    st.markdown("""
    <div class="main-header">
        <h1>🎤 演講逐字稿生成器</h1>
        <p>運用 AI Agent 技術，將投影片轉換為自然流暢的演講逐字稿</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 側邊欄 - API 設定
    with st.sidebar:
        st.header("⚙️ 設定")
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="請輸入您的 OpenAI API Key"
        )
        
        st.markdown("---")
        st.markdown("""
        ### 📋 使用步驟
        1. 輸入 API Key
        2. 上傳投影片 PDF
        3. 設定演講參數
        4. 點擊生成按鈕
        5. 下載逐字稿
        """)
    
    if not api_key:
        st.warning("⚠️ 請在左側輸入 OpenAI API Key")
        return
    
    # 初始化 Session State
    if 'pdf_processor' not in st.session_state:
        st.session_state.pdf_processor = PDFProcessor()
    if 'audio_analyzer' not in st.session_state:
        st.session_state.audio_analyzer = AudioAnalyzer(api_key)
    if 'transcript_generator' not in st.session_state:
        st.session_state.transcript_generator = TranscriptGenerator(api_key)
    if 'current_wpm' not in st.session_state:
        st.session_state.current_wpm = 200
    
    # 主要內容區域
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 步驟 1: 上傳投影片 PDF")
        pdf_file = st.file_uploader("選擇 PDF 檔案", type=['pdf'])
        
        if pdf_file:
            try:
                slides = st.session_state.pdf_processor.extract_slides(pdf_file)
                st.success(f"✅ 已載入 {len(slides)} 頁投影片")
            except Exception as e:
                st.error(f"❌ {str(e)}")
        
        st.markdown("---")
        st.subheader("⏱️ 步驟 2: 設定演講時間")
        duration = st.number_input("演講時長（分鐘）", min_value=1, max_value=180, value=10)
    
    with col2:
        st.subheader("🎙️ 步驟 3: 設定語速")
        speed_option = st.selectbox(
            "選擇語速",
            ["慢速 (150 字/分)", "中速 (200 字/分)", "快速 (250 字/分)", "自動分析"]
        )
        
        if speed_option == "自動分析":
            audio_file = st.file_uploader("上傳 20 秒音頻樣本", type=['mp3', 'm4a', 'wav'])
            if audio_file and st.button("🎵 開始分析語速"):
                try:
                    with st.spinner("分析中..."):
                        wpm = st.session_state.audio_analyzer.analyze_audio(audio_file)
                        st.session_state.current_wpm = int(wpm)
                        st.success(f"✅ 您的語速：{st.session_state.current_wpm} 字/分鐘")
                except Exception as e:
                    st.error(f"❌ {str(e)}")
        else:
            wpm_map = {"慢速 (150 字/分)": 150, "中速 (200 字/分)": 200, "快速 (250 字/分)": 250}
            st.session_state.current_wpm = wpm_map[speed_option]
    
    st.markdown("---")
    
    # 模型選擇
    st.subheader("🤖 步驟 4: 選擇 AI 模型")
    st.markdown('<div class="info-box">💡 <strong>GPT-5.1</strong> 具備最強大的多模態理解能力，能深度分析圖片與文字</div>', unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    with col3:
        model = st.selectbox(
            "AI 模型",
            ["GPT-5.1 ⭐ 推薦", "o3", "GPT-4o", "GPT-4o-mini"]
        )
        model_map = {
            "GPT-5.1 ⭐ 推薦": "gpt-5.1",
            "o3": "o3",
            "GPT-4o": "gpt-4o",
            "GPT-4o-mini": "gpt-4o-mini"
        }
        selected_model = model_map[model]
    
    with col4:
        style = st.selectbox("演講風格", ["活潑", "嚴肅", "激勵", "教學", "對話"])
    
    st.markdown("---")
    
    # 演講資訊
    st.subheader("📝 步驟 5: 填寫演講資訊")
    
    col5, col6 = st.columns(2)
    with col5:
        topic = st.text_input("演講題目", placeholder="例如：人工智慧在教育中的應用")
        language = st.selectbox(
            "輸出語言",
            ["繁體中文", "英文", "簡體中文", "日文", "韓文", "西班牙文", "法文", "德文"]
        )
    
    with col6:
        audience = st.text_input("目標聽眾", placeholder="例如：大學生、教師、科技愛好者")
        expert_role = st.text_input(
            "專家角色（選填）",
            placeholder="例如：資深AI研究員、教育心理學博士",
            help="AI 會扮演您指定的專家身份來撰寫逐字稿"
        )
    
    include_tips = st.checkbox("包含演講技巧建議（手勢、語氣、暫停等）", value=True)
    
    st.markdown("---")
    
    # 生成按鈕
    if st.button("🚀 生成逐字稿", type="primary"):
        if not pdf_file:
            st.error("❌ 請先上傳 PDF 投影片")
        elif not topic:
            st.error("❌ 請填寫演講題目")
        elif not audience:
            st.error("❌ 請填寫目標聽眾")
        else:
            try:
                with st.spinner("🔄 正在生成逐字稿，請稍候..."):
                    transcript = st.session_state.transcript_generator.generate_transcript(
                        slides=st.session_state.pdf_processor.slides_content,
                        target_duration=duration,
                        words_per_minute=st.session_state.current_wpm,
                        style=style,
                        topic=topic,
                        audience=audience,
                        language=language,
                        model_name=selected_model,
                        expert_role=expert_role if expert_role else None,
                        include_tips=include_tips
                    )
                    
                    st.success("✅ 逐字稿生成完成！")
                    
                    # 顯示逐字稿
                    st.markdown("### 📄 生成的逐字稿")
                    st.text_area("", transcript, height=400)
                    
                    # 下載按鈕
                    filename = f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    st.download_button(
                        label="📥 下載逐字稿",
                        data=transcript,
                        file_name=filename,
                        mime="text/plain"
                    )
                    
            except Exception as e:
                st.error(f"❌ 生成失敗：{str(e)}")


if __name__ == "__main__":
    main()
