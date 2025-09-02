@echo off
REM Resume Analyzer Deployment Script for Windows

echo 🚀 Starting Resume Analyzer Deployment

REM Check if .env file exists
if not exist .env (
    echo ❌ .env file not found. Please create it from .env.example
    exit /b 1
)

REM Build the Docker image
echo 🔨 Building Docker image...
docker build -t resume-analyzer:latest .

if %errorlevel% neq 0 (
    echo ❌ Docker build failed
    exit /b 1
)

REM Stop existing container if running
echo 🛑 Stopping existing container...
docker stop resume-analyzer-app 2>nul
docker rm resume-analyzer-app 2>nul

REM Run the new container
echo 🏃 Starting new container...
docker run -d ^
    --name resume-analyzer-app ^
    -p 8030:8030 ^
    --env-file .env ^
    --restart unless-stopped ^
    resume-analyzer:latest

if %errorlevel% equ 0 (
    echo ✅ Resume Analyzer deployed successfully!
    echo 🌐 Access the application at: http://localhost:8000
    echo 📊 Check container status: docker ps
    echo 📝 View logs: docker logs resume-analyzer-app
) else (
    echo ❌ Deployment failed
    exit /b 1
)