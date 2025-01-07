pip install fastapi uvicorn aiokafka python-multipart

cd video-transcription-app/
npm start 

cd transcription_translate
sudo su

docker compose up 

cd transcription_translate
source env/bin/activate

uvicorn src.main:app --reload



cd consumer/
source env/bin/activate
python3 consumer.py

alembic revision --autogenerate -m "create_relationship"
alembic upgrade head
pip3 freeze > requirements.txt
kafka-topics.sh --create --topic file-upload --bootstrap-server kafka:9092 --replication-factor 1 --partitions 1
kafka-topics.sh --create --topic video-transcription --bootstrap-server kafka:9092 --replication-factor 1 --partitions 1

https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-22-04
https://docs.docker.com/engine/install/ubuntu/

 https://www.youtube.com/watch?v=YpvcqxYiyNE&t=504s