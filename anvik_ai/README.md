NeRO 2.0 - Multi-Agent Deep Research Assistant
Overview
NeRO 2.0 (formerly Anvik.ai) is a production-ready, multi-agent research assistant with a Gradio frontend and FastAPI backend. It conducts in-depth research using Wikipedia and Google Scholar (via SerpAPI), powered by Google Gemini 2.5 Flash. Users can input topics via a web interface, view results (Wikipedia summary, paper details with links, citations, progress, proposal) in a conversational ChatGPT-like format.
Features

Frontend: Gradio interface for topic input and result display (Wikipedia summary, paper details with clickable URLs, APA/MLA citations, progress, proposal) in a chat-based format.
Backend: FastAPI server with consolidated agents in agents.py for Wikipedia fetching, Google Scholar searches, summarization, citation generation, and report compilation.
Real-Life Functions: Progress tracking, research proposal generation, and structured conversational output.

Installation
Clone the repository:
git clone <repository-url>
cd anvik_ai

Install Python:
Ensure Python 3.10 is installed:
python --version

Install dependencies:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

Set up environment variables:
Create a .env file in the root directory:
GEMINI_API_KEY=your_gemini_api_key
SERPAPI_KEY=your_serpapi_key


Obtain a Gemini API key from Google AI Studio.
Obtain a SerpAPI key from serpapi.com.

Running Locally
Start the application:

Start FastAPI server:cd C:\Users\91830\Desktop\appp\anvik_ai
uvicorn src.backend.api:app --host 0.0.0.0 --port 8000


Start Gradio interface in a new terminal:cd C:\Users\91830\Desktop\appp\anvik_ai
venv\Scripts\activate
python src\backend\interface.py

Access the application:
Open http://localhost:7860 in your browser.
Usage

Enter a research topic (e.g., "Artificial Intelligence in Healthcare") in the Gradio chat interface.
View the Wikipedia summary, research paper details (with clickable URLs), APA/MLA citations, progress, and proposal in the conversation.
Use the built-in clear button to reset the chat.
Logs are saved to logs/anvik_ai.log for troubleshooting.

Deployment (Render)
Create a Render account:
Sign up at render.com.
Set up a Web Service:

Create a new Web Service and connect your GitHub repository.
Configure:
Environment: Docker
Environment Variables:
GEMINI_API_KEY: Your Gemini API key
SERPAPI_KEY: Your SerpAPI key


Instance Type: Free tier


Deploy the service:
Trigger a deployment in Render.
Update CORS:
In src/backend/api.py, update allow_origins to include the Render URL (e.g., https://anvik-ai.onrender.com):
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7860", "https://anvik-ai.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Update Gradio API Calls:
In src/backend/interface.py, update the backend_url to the Render URL:
backend_url = "https://anvik-ai.onrender.com"
async with session.post(f"{backend_url}/research", json={"topic": topic}) as response:

Commit and push changes.
Access:
The Gradio interface will be available at <your-render-url>:7860.
Dependencies

aiohttp -> Asynchronous HTTP requests.
python-dotenv -> Environment variable management.
langchain -> Tool integration and prompt management.
langchain-community -> Wikipedia and other tools.
langchain-google-genai -> Gemini 2.5 Flash API integration.
pydantic -> Data modeling and validation.
fastapi -> API server.
uvicorn -> ASGI server for FastAPI.
gradio -> Web interface.

Notes

Ensure API keys have sufficient quotas.
Keep .env secure and do not commit to version control.
For scalability, consider adding rate limiting (e.g., fastapi-limiter) and caching (e.g., Redis).
Extend the system by adding agents in agents.py or customizing the Gradio interface in interface.py.
LaTeX and PDF/DOCX generation have been removed; the focus is now on a conversational interface.

License
MIT License
