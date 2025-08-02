from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from pydantic import BaseModel
from config.util import (
    get_youtube_id,
    get_data,
    get_chunks,
    get_vector_stores,
    generate_summary,
    generate_note,
    generate_question,
    generate_answer
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            
    allow_credentials=True,
    allow_methods=["*"],           
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="template")

VECTORSTORE = None
CACHED_VIDEO_ID = None
CHUNKS_CACHE = None
SUMMARY_CACHE = None

class URLRequest(BaseModel):
    url: str

class QuestionRequest(BaseModel):
    url: str
    question: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/ping")
async def ping():
    return {"message": "Service is live and loaded correctly!"}


@app.post("/summary")
async def summarize(payload: URLRequest):
    global SUMMARY_CACHE, CACHED_VIDEO_ID, CHUNKS_CACHE

    video_id = get_youtube_id(payload.url)

    try:
        if CACHED_VIDEO_ID != video_id:
            try:
                data = get_data(video_id)
            except Exception as e:
                raise HTTPException(404, f"Error fetching data for video ID {video_id}: {str(e)}")

            print("Type of data:", type(data))
            print("Repr of data:", repr(data))

            if data is None or not data:
                print("heLLO")
                return JSONResponse(status_code=404, content={"error": "Transcript not available or not in English."})

            CHUNKS_CACHE = get_chunks(data)
            SUMMARY_CACHE = generate_summary(CHUNKS_CACHE)
            CACHED_VIDEO_ID = video_id
            msg = "⚡ Summary generated and cached."

        else:
            if SUMMARY_CACHE:
                msg = "✅ Using cached summary."
            else:
                SUMMARY_CACHE = generate_summary(CHUNKS_CACHE)
                msg = "⚡ Summary generated and cached."

    except HTTPException as e:
        raise e  # Let FastAPI handle the error correctly

    return JSONResponse(content={"summary": SUMMARY_CACHE, "message": msg})


@app.post("/notes")
async def notes(payload: URLRequest):
    global CHUNKS_CACHE, CACHED_VIDEO_ID

    video_id = get_youtube_id(payload.url)
    try:
        if CACHED_VIDEO_ID != video_id or CHUNKS_CACHE is None:
            data = get_data(video_id)
            if not data:
                raise HTTPException(404, "Transcript not available or not in English.")
            CHUNKS_CACHE = get_chunks(data)
            CACHED_VIDEO_ID = video_id
            msg = "🗒️ Regenerated chunks for notes"
        else:
            msg = "✅ Using cached chunks for notes"
        notes_text = generate_note(CHUNKS_CACHE)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"error": e.detail})

    return JSONResponse(content={"notes": notes_text, "message": msg})

@app.post("/questions")
async def questions(payload: URLRequest):
    global CHUNKS_CACHE, CACHED_VIDEO_ID

    video_id = get_youtube_id(payload.url)
    try:
        if CACHED_VIDEO_ID != video_id or CHUNKS_CACHE is None:
            data = get_data(video_id)
            if not data:
                raise HTTPException(404, "Transcript not available or not in English.")
            CHUNKS_CACHE = get_chunks(data)
            CACHED_VIDEO_ID = video_id
            msg = "📄 Regenerated chunks for question generation"
        else:
            msg = "✅ Using cached chunks for questions"
        qs = generate_question(CHUNKS_CACHE)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"error": e.detail})

    return JSONResponse(content={"questions": qs, "message": msg})

@app.post("/answer")
async def answer(payload: QuestionRequest):
    global VECTORSTORE, CACHED_VIDEO_ID, CHUNKS_CACHE

    video_id = get_youtube_id(payload.url)
    try:
        if CACHED_VIDEO_ID != video_id or VECTORSTORE is None:
            data = get_data(video_id)
            if not data:
                raise HTTPException(404, "Transcript not available or not in English.")
            CHUNKS_CACHE = get_chunks(data)
            VECTORSTORE = get_vector_stores(CHUNKS_CACHE)
            CACHED_VIDEO_ID = video_id
            msg = "🔍 Regenerated vectorstore"
        else:
            msg = "✅ Using cached vectorstore"

        retriever = VECTORSTORE.as_retriever(search_kwargs={"k": 4})
        ans = generate_answer(payload.question, retriever)

    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"error": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    # <-- this return must be here, not indented under the except
    return JSONResponse(content={"answer_to_question": ans, "message": msg})



@app.get("/health")
async def health_check():
    return {
        "status": "OK",
        "version": "1.0.0",
        "vectorstore_loaded": VECTORSTORE is not None
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
