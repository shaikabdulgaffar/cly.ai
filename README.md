# CLY.AI

CLY.AI is a modern, web-based AI assistant platform featuring chat, lyrics search, and YouTube video summarization. Powered by Gemini AI and built with Django and React-style interactive UI, CLY.AI provides seamless, multi-mode conversations in a sleek, responsive interface.

---

## ✨ Features

- **AI Chat:**  
  Chat with a powerful Gemini-based assistant for general questions and conversations.

- **Lyrics Finder:**  
  Instantly fetch lyrics for any song using the Genius API.

- **YouTube Summarizer:**  
  Paste a YouTube link and receive an AI-generated summary of the video content.

- **Modern UI/UX:**  
  Responsive, mobile-friendly design with dark/light theme toggle.

- **Persistent Conversation:**  
  Chat history maintained per session, supports multi-turn dialogue.

- **Security:**  
  Escapes HTML in messages, robust backend authentication with Django REST Framework.

---

## 🛠️ Tech Stack

- **Frontend:**  
  - Vanilla JS (single-page app style)
  - CSS3 (custom, responsive, themeable)
  - HTML5

- **Backend:**  
  - Python 3, Django 4
  - Django REST Framework
  - PostgreSQL
  - Integration with:
    - Gemini AI API (for chat and summarization)
    - Genius API (for lyrics search)

---

## 📸 Screenshots

Dark Theme

![image](https://github.com/user-attachments/assets/5f5c7bca-5e4f-4f63-8279-0cae79af7464)


Light Theme

![image](https://github.com/user-attachments/assets/1dc87adb-d5c7-4879-8864-116acf8c929c)

---

## 🧑‍💻 Local Development

### Prerequisites

- Python 3.8+
- Node.js (for static asset management, optional)
- PostgreSQL
- [Genius API Token](https://genius.com/developers)
- Gemini AI API Key

### Setup

1. **Clone the repo:**
   ```sh
   git clone https://github.com/shaikabdulgaffar/cly.ai.git
   cd cly.ai
   ```

2. **Install Python dependencies:**
   ```sh
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**  
   Create a `.env` file in the root with:

   ```
   DJANGO_SECRET_KEY=your-secret-key
   POSTGRES_DB=your-db
   POSTGRES_USER=your-user
   POSTGRES_PASSWORD=your-password
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   GEMINI_API_KEY=your-gemini-api-key
   GENIUS_TOKEN=your-genius-token
   ```

4. **Migrate and run:**
   ```sh
   python manage.py migrate
   python manage.py runserver
   ```

5. **Access:**  
   Visit [http://localhost:8000](http://localhost:8000) in your browser.

---

## ⚙️ Project Structure

```
cly.ai/
├── ai_chatbot/          # Django project settings
├── chatbot/             # Django app (views, models, API)
├── static/              # Static JS/CSS (frontend)
├── templates/           # HTML templates
├── docs/                # Screenshots, documentation
├── manage.py
├── requirements.txt
└── README.md
```

---

## 📝 License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [Google Gemini AI](https://ai.google.com/gemini/)
- [Genius API](https://genius.com/developers)
- [Django](https://www.djangoproject.com/)
- [FontAwesome](https://fontawesome.com/)

---

## 📬 Contact

**Author:** Shaik Abdul Gaffar  
**GitHub:** [shaikabdulgaffar](https://github.com/shaikabdulgaffar)

---
