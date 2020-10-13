#!/usr/bin/env bash
docker start dynamodb
aws dynamodb create-table --table-name reservations_local --attribute-definitions AttributeName=reservation_id,AttributeType=S AttributeName=start_date_epoch,AttributeType=N --key-schema AttributeName=reservation_id,KeyType=HASH AttributeName=start_date_epoch,KeyType=RANGE --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 --endpoint-url http://localhost:8000
aws dynamodb list-tables --endpoint-url http://localhost:8000
