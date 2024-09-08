pip install fastapi uvicorn aiokafka python-multipart
cd transcription_translate
source env/bin/activate
pip3 freeze > requirements.txt
uvicorn src.main:app --reload
https://www.youtube.com/watch?v=YpvcqxYiyNE&t=504s

alembic revision --autogenerate -m "create_relationship"
alembic upgrade head

kafka-topics.sh --create --topic file-upload --bootstrap-server kafka:9092 --replication-factor 1 --partitions 1
kafka-topics.sh --create --topic video-transcription --bootstrap-server kafka:9092 --replication-factor 1 --partitions 1

https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-22-04
https://docs.docker.com/engine/install/ubuntu/
