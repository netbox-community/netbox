#!/bin/bash

docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD"
if [ $? -ne 0 ]; then
  echo "docker login failed."
  exit 1
fi

docker build -t "$DOCKER_REPOSITORY/$DOCKER_IMAGE_NAME:$DOCKER_TAG" .
if [ $? -ne 0 ]; then
  echo "docker build failed."
  exit 1
fi

docker push "$DOCKER_REPOSITORY/$DOCKER_IMAGE_NAME:$DOCKER_TAG"
if [ $? -ne 0 ]; then
  echo "docker push failed."
  exit 1
fi

exit 0
