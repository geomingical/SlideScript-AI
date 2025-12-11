"""
Speech Transcript Generator - Streamlit Version
Convert slide PDFs into professional speech transcripts using GPT-5.1/o3/GPT-4o models
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
    """Class for processing PDF slides"""
    
    def __init__(self):
        self.slides_content = []
    
    def extract_slides(self, pdf_file) -> List[Dict[str, str]]:
        """Extract content from each page of the PDF"""
        try:
            # Save uploaded PDF
            pdf_path = "/tmp/presentation.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(pdf_file.read())
            
            doc = fitz.open(pdf_path)
            
            if len(doc) == 0:
                doc.close()
                raise Exception("This PDF file does not contain any pages")
            
            slides = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text().strip()
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_data = pix.tobytes("png")
                
                slides.append({
                    "page": page_num + 1,
                    "text": text if text else "[No text content on this page]",
                    "image": base64.b64encode(img_data).decode()
                })
            
            doc.close()
            self.slides_content = slides
            return slides
            
        except Exception as e:
            raise Exception(f"PDF processing error: {str(e)}")


class AudioAnalyzer:
    """Analyze audio and calculate speech rate using GPT-4o Audio API"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.words_per_minute = None
    
    def _convert_to_mp3(self, audio_path: str) -> str:
        """Convert audio format to mp3"""
        try:
            audio = AudioSegment.from_file(audio_path)
            mp3_path = "/tmp/converted_audio.mp3"
            audio.export(mp3_path, format="mp3", bitrate="128k")
            return mp3_path
        except Exception as e:
            raise Exception(f"Audio format conversion error: {str(e)}")
    
    def analyze_audio(self, audio_file) -> float:
        """Analyze audio and calculate speech rate using GPT-4o Audio API"""
        try:
            # Save uploaded audio
            audio_path = "/tmp/audio_sample.m4a"
            with open(audio_path, 'wb') as f:
                f.write(audio_file.read())
            
            audio = AudioSegment.from_file(audio_path)
            duration_seconds = len(audio) / 1000.0
            
            if duration_seconds < 5:
                raise Exception("Audio duration too short (less than 5 seconds), suggest uploading around 20 seconds")
            if duration_seconds > 120:
                raise Exception("Audio duration too long (over 2 minutes), please upload a 20-60 second audio sample")
            
            # Convert to mp3
            mp3_path = self._convert_to_mp3(audio_path)
            
            # Transcribe using GPT-4o Audio API
            with open(mp3_path, 'rb') as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="zh"
                )
            
            text = transcription.text
            
            if not text or len(text.strip()) == 0:
                raise Exception("Unable to recognize audio content, please ensure audio is clear and contains speech")
            
            # Calculate word count
            char_count = len([c for c in text if c.strip() and not c.isspace()])
            wpm = (char_count / duration_seconds) * 60
            self.words_per_minute = wpm
            
            # Clean up temporary files
            if os.path.exists(audio_path):
                os.remove(audio_path)
            if os.path.exists(mp3_path):
                os.remove(mp3_path)
            
            return wpm
            
        except Exception as e:
            raise Exception(f"Audio analysis error: {str(e)}")


class TranscriptGenerator:
    """Generate speech transcript using OpenAI Vision models"""
    
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
        """Generate speech transcript"""
        try:
            if not slides or len(slides) == 0:
                raise Exception("No slide content, please upload a PDF file first")
            
            target_words = int(target_duration * words_per_minute)
            words_per_slide = target_words // len(slides)
            
            system_prompt = self._create_system_prompt(
                style, topic, audience, language, expert_role, words_per_slide, include_tips
            )
            
            tips_instruction = ""
            if include_tips:
                tips_instruction = """

【Speech Tips Suggestions】
Please include the following speech tips in appropriate places within the transcript (marked with [square brackets]):
- [Gesture: Open arms] - When emphasizing a key point
- [Gesture: Point to slide] - When explaining a chart
- [Tone: Raise volume] - For key messages
- [Tone: Slow down] - For important concepts
- [Pause 2-3 seconds] - During section transitions
- [Eye contact] - When interacting with the audience
- [Movement: Move to center stage] - During opening or closing
"""
            
            user_content = [
                {
                    "type": "text",
                    "text": f"""
Please generate a complete speech transcript based on the following slide images.

Speech Parameters:
- Total Duration: {target_duration} minutes
- Speech Rate: Approximately {int(words_per_minute)} words per minute
- Target Total Word Count: Approximately {target_words} words
- Suggested Words per Slide: Approximately {words_per_slide} words
- Output Language: {language}{tips_instruction}

Output Format Requirements:
Slide 1
[Speech content for slide 1]

Slide 2
[Speech content for slide 2]

...and so on

Please ensure:
1. Carefully observe the visual elements, charts, and text on each slide
2. The transcript for each page is natural and smooth, explaining the key points on the slide
3. Content flows smoothly with a clear opening and closing
4. Matches the specified speech style and tone
5. Total word count is around {target_words} words (allow 10% variance)
"""
                }
            ]
            
            # Add all slide images
            for slide in slides:
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{slide['image']}",
                        "detail": "high"
                    }
                })
            
            # Call OpenAI Vision API
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
                raise Exception("❌ API Key error, please check if your OpenAI API Key is correct")
            elif "rate limit" in error_msg.lower():
                raise Exception("❌ API request limit reached, please try again later")
            elif "quota" in error_msg.lower():
                raise Exception("❌ API quota exceeded, please check your OpenAI account balance")
            else:
                raise Exception(f"Transcript generation error: {error_msg}")
    
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
        """Create system prompt"""
        
        style_descriptions = {
            "Lively": "Use a relaxed, lively tone with appropriate interactive and humorous elements",
            "Serious": "Use a formal, professional tone maintaining academic rigor",
            "Motivational": "Use inspiring language full of positive energy and motivation",
            "Educational": "Use clear, easy-to-understand explanations, as if teaching students",
            "Conversational": "Use a conversational tone, as if talking face-to-face with the audience"
        }
        
        language_instructions = {
            "Traditional Chinese": "Output in Traditional Chinese",
            "English": "Output in English",
            "Simplified Chinese": "Output in Simplified Chinese",
            "Japanese": "Output in Japanese",
            "Korean": "Output in Korean",
            "Spanish": "Output in Spanish",
            "French": "Output in French",
            "German": "Output in German"
        }
        
        role_intro = ""
        if expert_role:
            role_intro = f"You are a {expert_role}, "
        
        style_desc = style_descriptions.get(style, "Use a natural and smooth tone")
        lang_inst = language_instructions.get(language, "Output in Traditional Chinese")
        
        tips_requirement = ""
        if include_tips:
            tips_requirement = """
7. Include speech tips suggestions in appropriate places, marked with [square brackets], including:
   - Gesture suggestions (e.g., open arms, point to slide, clench fist for emphasis)
   - Tone suggestions (e.g., raise volume, slow down, emphasize)
   - Pause timing (e.g., [Pause 2-3 seconds])
   - Body language (e.g., eye contact, movement, lean forward)
   These suggestions should blend naturally into the transcript to help the speaker better convey the message
"""
        
        return f"""
{role_intro}You are an experienced speaker and content creation expert.

Speech Topic: {topic}
Target Audience: {audience}
Speech Style: {style_desc}
Language Requirement: {lang_inst}

Your task is to create a natural, smooth, and engaging speech transcript based on the provided slide content.

Requirements:
1. Content must be faithful to the slides but expressed in spoken language
2. Approximately {words_per_slide} words per page, adjustable based on content importance
3. Opening must be attractive, closing must be powerful
4. Add transition phrases appropriately to ensure smooth flow
5. Match the specified speech style and target audience
6. Ensure content is professional and accurate, yet easy to understand{tips_requirement}
"""


# Streamlit Main Application
def main():
    st.set_page_config(
        page_title="Speech Transcript Generator",
        page_icon="🎤",
        layout="wide"
    )
    
    # Custom CSS
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
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎤 Speech Transcript Generator</h1>
        <p>Using AI Agent technology to convert slides into natural, smooth speech transcripts</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - API Settings
    with st.sidebar:
        st.header("⚙️ Settings")
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Please enter your OpenAI API Key"
        )
        
        st.markdown("---")
        st.markdown("""
        ### 📋 Usage Steps
        1. Enter API Key
        2. Upload Slide PDF
        3. Set Speech Parameters
        4. Click Generate Button
        5. Download Transcript
        """)
    
    if not api_key:
        st.warning("⚠️ Please enter OpenAI API Key in the sidebar")
        return
    
    # Initialize Session State
    if 'pdf_processor' not in st.session_state:
        st.session_state.pdf_processor = PDFProcessor()
    if 'audio_analyzer' not in st.session_state:
        st.session_state.audio_analyzer = AudioAnalyzer(api_key)
    if 'transcript_generator' not in st.session_state:
        st.session_state.transcript_generator = TranscriptGenerator(api_key)
    if 'current_wpm' not in st.session_state:
        st.session_state.current_wpm = 200
    
    # Main Content Area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 Step 1: Upload Slide PDF")
        pdf_file = st.file_uploader("Select PDF File", type=['pdf'])
        
        if pdf_file:
            try:
                slides = st.session_state.pdf_processor.extract_slides(pdf_file)
                st.success(f"✅ Loaded {len(slides)} slides")
            except Exception as e:
                st.error(f"❌ {str(e)}")
        
        st.markdown("---")
        st.subheader("⏱️ Step 2: Set Speech Duration")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=180, value=10)
    
    with col2:
        st.subheader("🎙️ Step 3: Set Speech Rate")
        speed_option = st.selectbox(
            "Select Speech Rate",
            ["Slow (150 wpm)", "Medium (200 wpm)", "Fast (250 wpm)", "Auto Analysis"]
        )
        
        if speed_option == "Auto Analysis":
            audio_file = st.file_uploader("Upload 20s audio sample", type=['mp3', 'm4a', 'wav'])
            if audio_file and st.button("🎵 Start Speech Rate Analysis"):
                try:
                    with st.spinner("Analyzing..."):
                        wpm = st.session_state.audio_analyzer.analyze_audio(audio_file)
                        st.session_state.current_wpm = int(wpm)
                        st.success(f"✅ Your Speech Rate: {st.session_state.current_wpm} words/min")
                except Exception as e:
                    st.error(f"❌ {str(e)}")
        else:
            wpm_map = {"Slow (150 wpm)": 150, "Medium (200 wpm)": 200, "Fast (250 wpm)": 250}
            st.session_state.current_wpm = wpm_map[speed_option]
    
    st.markdown("---")
    
    # Model Selection
    st.subheader("🤖 Step 4: Select AI Model")
    st.markdown('<div class="info-box">💡 <strong>GPT-5.1</strong> possesses the strongest multimodal understanding capabilities, enabling deep analysis of images and text</div>', unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    with col3:
        model = st.selectbox(
            "AI Model",
            ["GPT-5.1 ⭐ Recommended", "o3", "GPT-4o", "GPT-4o-mini"]
        )
        model_map = {
            "GPT-5.1 ⭐ Recommended": "gpt-5.1",
            "o3": "o3",
            "GPT-4o": "gpt-4o",
            "GPT-4o-mini": "gpt-4o-mini"
        }
        selected_model = model_map[model]
    
    with col4:
        style = st.selectbox("Speech Style", ["Lively", "Serious", "Motivational", "Educational", "Conversational"])
    
    st.markdown("---")
    
    # Speech Information
    st.subheader("📝 Step 5: Fill in Speech Info")
    
    col5, col6 = st.columns(2)
    with col5:
        topic = st.text_input("Speech Topic", placeholder="e.g., Application of AI in Education")
        language = st.selectbox(
            "Output Language",
            ["Traditional Chinese", "English", "Simplified Chinese", "Japanese", "Korean", "Spanish", "French", "German"]
        )
    
    with col6:
        audience = st.text_input("Target Audience", placeholder="e.g., University Students, Teachers, Tech Enthusiasts")
        expert_role = st.text_input(
            "Expert Role (Optional)",
            placeholder="e.g., Senior AI Researcher, PhD in Educational Psychology",
            help="AI will act as the expert you specify to write the transcript"
        )
    
    include_tips = st.checkbox("Include speech tips suggestions (gestures, tone, pauses, etc.)", value=True)
    
    st.markdown("---")
    
    # Generate Button
    if st.button("🚀 Generate Transcript", type="primary"):
        if not pdf_file:
            st.error("❌ Please upload PDF slides first")
        elif not topic:
            st.error("❌ Please fill in the speech topic")
        elif not audience:
            st.error("❌ Please fill in the target audience")
        else:
            try:
                with st.spinner("🔄 Generating transcript, please wait..."):
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
                    
                    st.success("✅ Transcript Generation Complete!")
                    
                    # Display Transcript
                    st.markdown("### 📄 Generated Transcript")
                    st.text_area("", transcript, height=400)
                    
                    # Download Button
                    filename = f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    st.download_button(
                        label="📥 Download Transcript",
                        data=transcript,
                        file_name=filename,
                        mime="text/plain"
                    )
                    
            except Exception as e:
                st.error(f"❌ Generation Failed: {str(e)}")


if __name__ == "__main__":
    main()