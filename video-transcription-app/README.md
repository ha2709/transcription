cd video-transcription-app/
npm start

cd video_transcription_project/
source env/bin/activate

pip freeze > requirements.txt

sudo docker-compose up -d
python manage.py run_kafka_consumer
docker-compose up --build -d
docker exec -it video_transcription_project-kafka-1 /bin/bash
kafka-topics.sh --create --topic file-upload --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
kafka-topics.sh --list --bootstrap-server localhost:9092
https://www.instagram.com/reel/C7wuY7Xghfc/?igsh=YmQ3dDhjcWdybWlk
pip3 freeze > requirements.txt 
chmod -R 777 /var/run/docker.sock
http://localhost:8000/media/download/output-7f11a8d9-0fac-4f0a-b1d2-07f38195d7a1.mp4
python manage.py makemigrations
python manage.py migrate
sudo systemctl stop postgresql
sudo kill 'sudo lsof -t -i:5432'
sudo systemctl start postgresql
sudo lsof -t -i:5432
sudo lsof -t -i:9002
sudo docker logs video_transcription_project-zookeeper-1
sudo docker-compose down
sudo docker-compose up -d




https://www.youtube.com/watch?v=9bZkp7q19f0

https://github.com/openai/whisper
https://github.com/x404xx/Fb-Down
pip install -r requirements.txt
