# 🎤 SlideScript AI

> **AI-Powered Presentation Speech Generator** - Transform your slides into natural, professional speech transcripts using advanced AI models.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5.1-green.svg)](https://openai.com/)

---

## ✨ Features

- 📊 **Smart Slide Analysis** - Automatically parses PDF presentation content with vision AI
- 🎙️ **Speech Rate Detection** - Upload a 20-second audio sample for automatic speed calculation
- 🎭 **Multiple Speech Styles** - Supports lively, serious, motivational, educational, and conversational styles
- 🌐 **Multilingual Support** - Generate transcripts in 8 languages:
  - 繁體中文 (Traditional Chinese)
  - English
  - 简体中文 (Simplified Chinese)
  - 日本語 (Japanese)
  - 한국어 (Korean)
  - Español (Spanish)
  - Français (French)
  - Deutsch (German)
- 🤖 **Multiple AI Models** - Choose from GPT-5.1, o3, GPT-4o, or GPT-4o-mini
- 👨‍🏫 **Expert Role Playing** - AI generates content from specific expert perspectives
- 💡 **Speech Technique Suggestions** - Includes gestures, tone, and pause recommendations
- 📥 **One-Click Download** - Export transcripts in TXT format

---

## � Language Versions

This project provides **two notebook versions** for different users:

- **`presentation_transcript_generator_zh-TW.ipynb`** - Traditional Chinese (繁體中文)
  - Code comments and docstrings in Traditional Chinese
  - For Taiwanese and Chinese-speaking developers
  
- **`presentation_transcript_generator_en.ipynb`** - English
  - Code comments and docstrings in English
  - For international developers

> **Note**: Both versions have **identical functionality**. All Chinese UI elements are preserved for the best user experience.

---

## 🚀 Quick Start

### Option 1: Google Colab (Recommended for Beginners)

1. Open the notebook in Google Colab:
   - **Chinese version**: Upload `presentation_transcript_generator_zh-TW.ipynb`
   - **English version**: Upload `presentation_transcript_generator_en.ipynb`
   - Open with Google Colab
   
2. Set your OpenAI API Key:
   - Use Colab Secrets (recommended): Add `GPT_API_KEY` in Secrets
   - Or enter manually when prompted

3. Run all cells and follow the interactive UI

### Option 2: Local Installation (Python Required)

#### Prerequisites
- Python 3.10 or higher
- FFmpeg (for audio processing)
- OpenAI API Key

#### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/slidescript-ai.git
   cd slidescript-ai
   ```

2. **Install FFmpeg**
   
   macOS:
   ```bash
   brew install ffmpeg
   ```
   
   Ubuntu/Debian:
   ```bash
   sudo apt-get update
   sudo apt-get install ffmpeg
   ```
   
   Windows:
   - Download from [FFmpeg website](https://ffmpeg.org/download.html)
   - Add to system PATH

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Streamlit app**
   ```bash
   streamlit run app.py
   ```

5. **Access the app**
   - Open your browser to `http://localhost:8501`
   - Enter your OpenAI API Key in the sidebar
   - Start generating transcripts!

---

## 📖 Usage Guide

### Step-by-Step Instructions

1. **Upload PDF Slides**
   - Click "選擇 PDF 檔案" to upload your presentation
   - Maximum file size: 50MB
   - Supported format: PDF

2. **Set Speech Duration**
   - Enter your target presentation length (1-180 minutes)

3. **Configure Speech Rate**
   - Choose from preset speeds: Slow (150), Medium (200), Fast (250)
   - Or upload a 20-second audio sample for automatic analysis

4. **Select AI Model**
   - **GPT-5.1** ⭐ (Recommended): Best multimodal understanding
   - **o3**: Strong reasoning for complex logic
   - **GPT-4o**: Balanced performance
   - **GPT-4o-mini**: Fast and economical

5. **Choose Speech Style**
   - Lively (活潑)
   - Serious (嚴肅)
   - Motivational (激勵)
   - Educational (教學)
   - Conversational (對話)

6. **Fill in Details**
   - **Topic**: Your presentation subject
   - **Audience**: Target audience (e.g., university students, professionals)
   - **Language**: Output language (8 options available)
   - **Expert Role** (Optional): AI will assume this expert identity
   - **Include Tips**: Check to add speech technique suggestions

7. **Generate & Download**
   - Click "生成逐字稿" to generate
   - Review the transcript
   - Download as TXT file

---

## 🎯 Use Cases

- 📚 **Academic Presentations** - Convert research slides into lecture scripts
- 💼 **Business Pitches** - Create professional presentation narratives
- 🎓 **Educational Content** - Transform teaching materials into engaging scripts
- 🌍 **Multilingual Events** - Generate transcripts in multiple languages
- 🎤 **Conference Talks** - Prepare speaker notes with timing guidance

---

## 🤖 AI Models Comparison

| Model | Best For | Speed | Cost |
|-------|----------|-------|------|
| **GPT-5.1** ⭐ | Deep image-text analysis, multimodal understanding | Medium | High |
| **o3** | Complex reasoning, logical analysis | Slow | High |
| **GPT-4o** | Balanced performance, general use | Fast | Medium |
| **GPT-4o-mini** | Quick results, basic needs | Very Fast | Low |

---

## 🛠️ Technical Details

### Architecture
- **Frontend**: Streamlit (local) / IPyWidgets (Colab)
- **PDF Processing**: PyMuPDF (fitz)
- **Audio Analysis**: OpenAI Whisper-1 API
- **AI Models**: OpenAI GPT-5.1/o3/GPT-4o/GPT-4o-mini
- **Audio Conversion**: pydub + FFmpeg

### API Requirements
- OpenAI API account with available credits
- Supported models: gpt-5.1, o3, gpt-4o, gpt-4o-mini
- Audio API: whisper-1

---

## 📋 Requirements

### Python Packages
```
openai>=1.12.0
pymupdf>=1.23.0
pillow>=10.0.0
pydub>=0.25.1
streamlit>=1.31.0
```

### System Requirements
- Python 3.10+
- FFmpeg (for audio processing)
- 4GB+ RAM recommended
- Internet connection for API calls

---

## 🔐 Security & Privacy

- **API Keys**: Never commit API keys to version control
- **Data Privacy**: All processing is done via OpenAI API (subject to their terms)
- **Local Files**: Temporary files are stored in `/tmp/` and cleaned up after use
- **Best Practice**: Use environment variables or secrets management for API keys

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [OpenAI API](https://openai.com/)
- PDF processing powered by [PyMuPDF](https://pymupdf.readthedocs.io/)
- Audio handling by [pydub](https://github.com/jiaaro/pydub)
- UI framework: [Streamlit](https://streamlit.io/)

---

## 📞 Support

If you encounter any issues or have questions:

- 🐛 [Report a Bug](https://github.com/yourusername/slidescript-ai/issues)
- 💡 [Request a Feature](https://github.com/yourusername/slidescript-ai/issues)
- 📧 Contact: your.email@example.com

---

## 🌟 Star History

If you find this project helpful, please consider giving it a star! ⭐

---

**Made with ❤️ by a passionate developer using top-tier programming principles and UX design**

**Last Updated**: December 2025
