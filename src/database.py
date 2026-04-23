# pip install mysql-connector-python python-dotenv
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def getDatabaseConnection():
    """MySQL 데이터베이스 연결을 생성하고 반환합니다."""
    dbConnection = mysql.connector.connect(
        host = os.getenv("MYSQL_HOST"),
        user = os.getenv("MYSQL_USER"),
        password = os.getenv("MYSQL_PASSWORD"),
        database = os.getenv("MYSQL_DATABASE"),
        port = os.getenv("MYSQL_PORT")
    )
    return dbConnection

def initializeDatabase():
    """테이블이 없을 경우 생성합니다."""
    dbConnection = getDatabaseConnection()
    cursor = dbConnection.cursor()
    
    # 명시적인 반복문 대신 단일 쿼리로 처리하거나, 여러 테이블일 경우 루프를 사용합니다.
    createTableQuery = """
    CREATE TABLE IF NOT EXISTS AnalysisResults (
        id INT AUTO_INCREMENT PRIMARY KEY,
        fileName VARCHAR(255),
        question TEXT,
        answer TEXT,
        usedModel VARCHAR(50),
        createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(createTableQuery)
    dbConnection.commit()
    cursor.close()
    dbConnection.close()

def saveAnalysisResult(fileName: str, question: str, answer: str, usedModel: str):
    """분석 결과를 DB에 저장합니다."""
    dbConnection = getDatabaseConnection()
    cursor = dbConnection.cursor()
    
    insertQuery = "INSERT INTO AnalysisResults (fileName, question, answer, usedModel) VALUES (%s, %s, %s, %s)"
    values = (fileName, question, answer, usedModel)
    
    cursor.execute(insertQuery, values)
    dbConnection.commit()
    
    cursor.close()
    dbConnection.close()

if __name__ == "__main__":
    initializeDatabase()
    print("Database initialized successfully.")
