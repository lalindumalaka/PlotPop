# PlotPOP

PlotPOP is a full-stack AI web application that generates creative movie storylines based on user input. Users can select a movie genre, specify the desired runtime, and the number of main characters. The app uses OpenAI's GPT model to generate a compelling and imaginative storyline suitable for a short film or feature-length production.

## Features

- Genre selection (Action, Romance, Sci-Fi, Comedy, Horror, etc.)
- Runtime input (in minutes)
- Character count input
- AI-generated movie storyline
- Clean, responsive UI
- Real-time feedback and display of results

## Tech Stack

- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Backend:** Python, FastAPI, Pydantic, OpenAI API, CORS

## Project Structure

```
movie-story-bot/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── README.md
└── run.sh (optional)
```

## Setup Instructions

### Backend

1. Navigate to the `backend` directory.
2. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the FastAPI server:
   ```
   uvicorn main:app --reload
   ```

### Frontend

Open `frontend/index.html` in your browser.

---

## Outcome

Users receive a unique, AI-generated movie plot tailored to their specifications with just a few clicks. Great for writers, filmmakers, and movie fans!
