#!/bin/bash

# Wait for Kafka to be ready
sleep 10

# Create topics
kafka-topics.sh --create --topic file-upload --bootstrap-server kafka:9092 --replication-factor 1 --partitions 1
kafka-topics.sh --create --topic video-transcription --bootstrap-server kafka:9092 --replication-factor 1 --partitions 1
