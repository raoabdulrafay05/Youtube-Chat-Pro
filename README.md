🎥***YouTube Chat Pro***
An AI-powered tool built on RAG (Retrieval-Augmented Generation) architecture that helps you learn smarter from YouTube videos. 📚💡🤖

🚀 **Overview**
YouTube Chat Pro enables users to extract meaningful insights from YouTube videos by leveraging advanced AI techniques. Simply input a video URL, and the system provides:

📄 **Summaries** – Concise overviews of video content.

📝 **Structured Notes** – Useful notes generated from the video to support revision or reference.

❓ **Question Generation** – Critical questions designed to enhance comprehension.

💬 **Interactive Q&A** – Ask custom questions and get context-aware answers instantly.

🧠 **Tech Stack**

🔧 **Backend**

**LangChain** – Orchestrates the RAG pipeline and enables modular LLM operations.

**FastAPI** – Provides a fast, async web framework for serving the API.

**OpenAI Embeddings** – Used for converting video transcripts into vector representations for retrieval.

**RecursiveCharacterTextSplitter** – Efficiently splits large text into meaningful chunks for better context handling.

**FAISS Database** – Custom-built vector database used for storing and retrieving processed video data.

💻 **Frontend**
HTML, CSS, JavaScript – Responsive UI to load videos, interact with the app, and display results dynamically.

📂 **Future Improvements**

🔍 Add support for video search by topic

🌍 Multilingual transcript support

🧠 Fine-tuning for domain-specific content (e.g., medical, legal)

📌 **Getting Started**
You can run YouTube Chat Pro locally using Docker:
**docker pull abdulrafay05/youtubechatpro**
