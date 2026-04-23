/**
 * 실행 전 필수 설치: npm install express multer axios cors
 * 실행 방법: node server.js
 */

const express = require('express');
const multer = require('multer');
const axios = require('axios');
const cors = require('cors');
const path = require('path');
const FormData = require('form-data');
const fs = require('fs');

const app = express();
const port = 3000;

// 모든 Origin 허용
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// multer 설정: 메모리에 파일 임시 저장
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

/**
 * FastAPI 서버로 분석 요청을 전달하는 프록시 함수
 * @param {Object} file - 업로드된 이미지 파일
 * @param {string} question - 사용자 질문
 */
async function proxyToAnalyze(file, question) {
    try {
        const formData = new FormData();
        formData.append('file', file.buffer, {
            filename: file.originalname,
            contentType: file.mimetype,
        });
        formData.append('question', question);

        // FastAPI 서버(8000번 포트)로 데이터 전송
        const response = await axios.post('http://localhost:8000/analyze', formData, {
            headers: {
                ...formData.getHeaders(),
            },
        });

        return response.data;
    } catch (error) {
        console.error('FastAPI Error:', error.message);
        throw new Error('AI 분석 서버와 통신 중 오류가 발생했습니다.');
    }
}

/**
 * 분석 요청 API 엔드포인트
 */
app.post('/analyze', upload.single('image'), async (req, res) => {
    try {
        const imageFile = req.file;
        const userQuestion = req.body.question;

        if (!imageFile) {
            return res.status(400).json({ success: false, message: '이미지 파일이 없습니다.' });
        }

        // FastAPI 서버에 분석 요청
        const result = await proxyToAnalyze(imageFile, userQuestion);
        
        // 결과 반환
        res.json(result);
    } catch (error) {
        // 에러 발생 시 공통 형식으로 응답
        res.status(500).json({ 
            success: false, 
            message: error.message || '서버 내부 오류가 발생했습니다.' 
        });
    }
});

// 서버 시작
app.listen(port, () => {
    console.log(`서버가 구동되었습니다: http://localhost:${port}`);
});
