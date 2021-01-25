#!/usr/bin/env bash

init_tables(){
  docker run --name gcsc-ddb -d -p 8000:8000 amazon/dynamodb-local
  aws dynamodb create-table --endpoint-url http://localhost:8000 \
    --table-name reservations-table_local \
    --attribute-definitions AttributeName=reservation_guid,AttributeType=S AttributeName=epoch_start,AttributeType=N AttributeName=user_guid,AttributeType=S \
    --key-schema AttributeName=reservation_guid,KeyType=HASH AttributeName=epoch_start,KeyType=RANGE \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --global-secondary-indexes "
    [
      {
        \"IndexName\": \"UserGUIDIndex\",
        \"KeySchema\": [{\"AttributeName\": \"user_guid\", \"KeyType\": \"HASH\"}],
        \"Projection\": {\"ProjectionType\": \"ALL\"},
        \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
      }
    ]"
  aws dynamodb list-tables --endpoint-url http://localhost:8000
}

export AWS_PROFILE=jgularte

if [ "$1" == "tables" ]; then
  init_tables
elif [ "$1" == "api" ]; then

  if [ "$2" == "local" ]; then
    init_tables
    export RUN_ENV=local
  elif [ "$2" == "sandbox" ]; then
    export RUN_ENV=sandbox
  elif [ "$2" == "prod" ]; then
    export RUN_ENV=prod
  else
    echo "Parameter 2 should be local, sandbox, or prod."
    exit
  fi

  cd source
  chalice local --port 8001
else
    echo "Parameter 1 should be tables or api (accompanied by the run_env)"
    exit
fi