# AI 프로젝트 개발 표준 가이드 (Model Serving)
## 1. 기본 원칙
- **언어:** 모든 답변 및 주석은 **한국어** (코드는 영문).
- **톤:** 친절하고 전문적인 IT 교육자 톤 유지.
- **환경:** Python 3.12.10 필수.
## 2. 핵심 아키텍처 및 모델 스위칭
- **Model Selector:** `config.py` 또는 환경 변수를 통해 `GPT`와 `OLLAMA` 모드를 전환할 수 있어야 함.
- **Ollama 설정:** 로컬 GPU를 활용하며 `gemma4:e2b` 모델을 기본으로 사용.
- **Stateless 구조:** API는 요청마다 독립적으로 처리하며, 데이터는 MySQL에 영구 저장.
## 3. 프로젝트 구조 (ai_project)
/ai_project
├── app.py (FastAPI 실행 및 모델 서빙 통합 진입점)
├── .env (GPT/Ollama 설정 및 API Key 관리)
├── requirements.txt (의존성 패키지 목록)
├── database.py (MySQL 연동 및 쿼리 관리)
├── dataset/ (이미지 및 학습 데이터 저장소)
├── src/
│   └── database.py (실제 DB 로직)
└── AI_GUIDE.md (현재 가이드 파일)

## 4. 지원 모델
- **OLLAMA:** 로컬 GPU 활용, `gemma4:e2b` 모델 기본 사용.
- **CHANDRA:** OCR 전용 엔진, 텍스트 추출 및 문서 분석.
- **GPT:** OpenAI `gpt-4o` 모델 활용, 고성능 비전 분석.
## 4. 코딩 스타일 (Strict)
- **명명 규칙:** 변수명과 함수명은 `camelCase` 사용.
- **반복문:** 리스트 컴프리헨션 사용 금지. 반드시 `for i in range(0, len(obj)):` 형식을 취할 것.
- **조건문:** `if-elif-else`를 명확히 구분하여 작성.
- **함수:** 모든 함수는 `def funcName(param):` 뒤에 `""" 함수 설명 """`을 필수로 작성.
- **파일 경로:** `os.path` 대신 `os.listdir`와 경로 조작 함수를 적절히 혼용하여 관리.
## 5. 보안 및 에러 처리
- **CORS:** 모든 Origin/Method/Header 허용 (`*`).
- **예외 처리:** 전체 로직을 `try-except`로 감싸고, 에러 발생 시 아래 JSON 반환.
- 형식: `{"success": false, "message": "에러 내용"}`

