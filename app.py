import os
import base64
import io
import torch
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from PIL import Image
import ollama
from openai import OpenAI

from transformers import AutoModelForImageTextToText, AutoProcessor
from chandra.model.hf import generate_hf
from chandra.model.schema import BatchInputItem
from chandra.output import parse_markdown

# 커스텀 DB 모듈 로드
from src.database import saveAnalysisResult, initializeDatabase

load_dotenv()

app = FastAPI()
chandraModel = None

# 가이드 5: 모든 Origin/Method/Header 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openAiClient = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encodeImageToBase64(imageBytes):
    """ 이미지를 Base64 문자열로 인코딩합니다. """
    return base64.b64encode(imageBytes).decode('utf-8')

@app.on_event("startup")
def onStartup():
    """ 서버 시작 시 데이터베이스와 Chandra 모델을 초기화합니다. """
    global chandraModel

    initializeDatabase()

    # GPU 사용 가능 여부 확인 출력
    print(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU Device: {torch.cuda.get_device_name(0)}")
    else:
        print("Warning: GPU not detected. Using CPU instead.")

    chandraModel = AutoModelForImageTextToText.from_pretrained(
        "datalab-to/chandra-ocr-2",
        dtype=torch.bfloat16,
        device_map="auto",
    )

    chandraModel.eval()

    chandraModel.processor = AutoProcessor.from_pretrained(
        "datalab-to/chandra-ocr-2"
    )

    chandraModel.processor.tokenizer.padding_side = "left"

@app.post("/analyze")
async def analyzeImage(question: str = Form(...), file: UploadFile = File(...), modelSelect: str = Form("OLLAMA")):
    """ 
    이미지를 분석하여 결과를 반환합니다. 
    OLLAMA, GPT, CHANDRA 세 가지 모델을 지원합니다.
    """
    try:
        fileBytes = await file.read()
        fileName = file.filename
        finalAnswer = ""
        
        # 가이드 4: if-elif-else 명확히 구분
        if modelSelect == "OLLAMA":
            # Ollama 로직
            response = ollama.generate(
                model='gemma4:e2b',
                prompt=question,
                images=[fileBytes]
            )
            finalAnswer = response['response']
            
        elif modelSelect == "GPT":
            # GPT-4o Vision 로직
            base64Image = encodeImageToBase64(fileBytes)
            # 파일의 콘텐츠 타입(image/png, image/jpeg 등)을 그대로 사용
            mimeType = file.content_type
            
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
                                    "url": f"data:{mimeType};base64,{base64Image}"
                                }
                            }
                        ]
                    }
                ]
            )
            finalAnswer = response.choices[0].message.content

        elif modelSelect == "CHANDRA":
            pilImage = Image.open(io.BytesIO(fileBytes)).convert("RGB")

            batch = [
                BatchInputItem(
                    image=pilImage,
                    prompt_type="ocr_layout"
                )
            ]

            result = generate_hf(batch, chandraModel)[0]

            finalAnswer = parse_markdown(result.raw)

        else:
            finalAnswer = "지원하지 않는 모델입니다."

        # DB 저장
        saveAnalysisResult(fileName, question, finalAnswer, modelSelect)
        
        return {
            "success": True,
            "fileName": fileName,
            "model": modelSelect,
            "answer": finalAnswer
        }
        
    except Exception as error:
        # 가이드 5: 에러 발생 시 지정된 JSON 반환
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(error)}
        )

if __name__ == "__main__":
    # 가이드에 따라 camelCase 준수 및 명확한 실행
    uvicorn.run(app, host="0.0.0.0", port=8000)
