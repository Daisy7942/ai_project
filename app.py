# %% [markdown]
# # Analysis Server
# ### pip install fastapi uvicorn ollama openai python-multipart python-dotenv mysql-connector-python pillow nest-asyncio

# %%
import os
import base64
import io
from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import uvicorn
import nest_asyncio
from PIL import Image
import ollama
from openai import OpenAI

# 커스텀 DB 모듈 로드
import sys
sys.path.append('..')
from src.database import saveAnalysisResult, initializeDatabase

load_dotenv()
nest_asyncio.apply()

app = FastAPI()
openAiClient = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encodeImageToBase64(imageBytes: bytes) -> str:
    return base64.b64encode(imageBytes).decode('utf-8')

@app.on_event("startup")
def onStartup():
    initializeDatabase()

@app.post("/analyze")
async def analyzeImage(question: str = Form(...), file: UploadFile = File(...)):
    usedModel = os.getenv("USE_MODEL", "OLLAMA")
    fileBytes = await file.read()
    fileName = file.filename
    
    finalAnswer = ""
    
    try:
        if usedModel == "OLLAMA":
            # Ollama 로직: gemma4:e2b 사용 (Vision 지원 모델인 llava 등을 사용하는 것이 일반적이나 요청대로 처리)
            # gemma 모델이 이미지를 지원하지 않을 경우를 대비해 텍스트와 이미지 바이트를 함께 전달하는 구조 유지
            response = ollama.generate(
                model='gemma4:e2b',
                prompt=question,
                images=[fileBytes]
            )
            finalAnswer = response['response']
            
        elif usedModel == "GPT":
            # GPT-4o Vision 로직
            base64Image = encodeImageToBase64(fileBytes)
            response = openAiClient.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64Image}"
                                }
                            }
                        ]
                    }
                ]
            )
            finalAnswer = response.choices[0].message.content

        # DB 저장 (명시적 로직)
        saveAnalysisResult(fileName, question, finalAnswer, usedModel)
        
        return {
            "status": "success",
            "fileName": fileName,
            "model": usedModel,
            "answer": finalAnswer
        }
        
    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(error)}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


