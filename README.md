# How to Run All Services

## 1. Start the Frontend App

```
cd video-transcription-app/
npm start 
```

## 2. Start Backend Services (Docker) 

```
cd transcription_translate
sudo su
docker compose up 
```

## 3. Start FastAPI Backend (Manual)

```
cd transcription_translate
source env/bin/activate
uvicorn src.main:app --reload
```

## 4. Start Consumer Service

```
cd consumer/
source env/bin/activate
python3 consumer.py
```  

Make sure all Python environments (env/) are already set up. If not, run:

```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

```
