#!/bin/bash
docker-compose down -t 0
docker-compose up --remove-orphans --build