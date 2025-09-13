# app.py
import os
import json
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from auth import get_authorization_url, exchange_code_for_credentials, credentials_from_json
from gdocs import list_google_docs, fetch_doc_text
from rag import RAGPipeline

# load env
load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
REDIRECT_URI = os.getenv("REDIRECT_URI", f"{BASE_URL}/oauth2callback")

app = FastAPI()
templates = Jinja2Templates(directory="frontend")
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# in-memory session store (for demo). For production use proper session store/DB.
SESSION_STORE = {}
rag = RAGPipeline()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "auth_url": f"/login"})

@app.get("/login")
def login():
    auth_url = get_authorization_url(REDIRECT_URI)
    return RedirectResponse(url=auth_url)

@app.get("/oauth2callback")
def oauth2callback(code: str = None, error: str = None):
    import uuid

    if error:
        print("OAuth returned error:", error)
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")

    if not code:
        print("No code returned from Google OAuth")
        raise HTTPException(status_code=400, detail="No code returned from Google OAuth")

    try:
        # Exchange code for credentials
        creds_json = exchange_code_for_credentials(REDIRECT_URI, code)
        print("Token fetched successfully:", creds_json)
    except Exception as e:
        print("Failed to fetch token:", e)
        raise HTTPException(status_code=500, detail=f"Token exchange failed: {e}")

    # Create a session
    session_id = str(uuid.uuid4())
    SESSION_STORE[session_id] = creds_json

    # Redirect to frontend with session_id
    return RedirectResponse(url=f"/?session_id={session_id}")


@app.get("/api/list_docs")
def api_list_docs(session_id: str):
    creds = SESSION_STORE.get(session_id)
    if not creds:
        raise HTTPException(401, "No session found. Please log in.")
    files = list_google_docs(creds)
    return JSONResponse(content={"files": files})

@app.post("/api/add_doc")
async def api_add_doc(session_id: str = Form(...), doc_id: str = Form(...)):
    creds = SESSION_STORE.get(session_id)
    if not creds:
        raise HTTPException(401, "Session expired or missing.")
    text = fetch_doc_text(doc_id, creds)
    rag.add_document(text, doc_id=doc_id)
    return {"status": "ok", "message": f"Document {doc_id} added. Chunks total: {len(rag.chunks)}"}

@app.post("/api/chat")
async def api_chat(query: str = Form(...)):
    # Here we only run retrieval and return passages. You may integrate LLM.
    result = rag.answer(query, k=3, threshold=1.2)
    if result["found_in_docs"]:
        # return extracted passages as the basis of the answer
        passages = [{"text": p, "distance": d} for p, d in result["passages"]]
        return {"source": "docs", "found": True, "passages": passages, "answer": f"Based on your documents: {passages[0]['text']}"}
    else:
        # explicit fallback behavior
        # Provide fallback message and attempt to answer from general knowledge (not using user docs)
        fallback_text = "Answer not found in selected documents. (Fallback answer from general knowledge not implemented in this demo.)"
        # If you want to integrate an LLM (OpenAI), call it here to produce fallback_answer
        return {"source": "fallback", "found": False, "passages": [], "answer": fallback_text}
