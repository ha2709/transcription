```
cd video-transcription-app/
npm start 
```

```
cd transcription_translate
sudo su
docker compose up 
```
```
cd transcription_translate
source env/bin/activate
uvicorn src.main:app --reload
```

```
cd consumer/
source env/bin/activate
python3 consumer.py
```  