pip install fastapi uvicorn aiokafka python-multipart

source env/bin/activate

uvicorn src.main:app --reload
https://www.youtube.com/watch?v=YpvcqxYiyNE&t=504s

alembic revision --autogenerate -m "create_relationship"`
kafka-topics.sh --create --topic file-upload --bootstrap-server kafka:9092 --replication-factor 1 --partitions 1
kafka-topics.sh --create --topic video-transcription --bootstrap-server kafka:9092 --replication-factor 1 --partitions 1
