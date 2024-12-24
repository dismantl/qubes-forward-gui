#!/bin/bash
docker-compose down -t 1
docker-compose up --remove-orphans --build