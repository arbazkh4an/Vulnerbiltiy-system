#!/bin/bash
set -e

echo "=== Docker Compose Test Suite ==="

echo ""
echo "Test 1: Validating docker-compose.yml..."
if docker-compose config > /dev/null 2>&1; then
    echo "PASS: docker-compose.yml is valid"
else
    echo "FAIL: docker-compose.yml validation failed"
    docker-compose config
    exit 1
fi

echo ""
echo "Test 2: Starting postgres and redis..."
docker-compose up -d postgres redis

echo "Waiting for services to become healthy..."
sleep 10

echo ""
echo "Test 3: Checking postgres connectivity on port 5432..."
if docker-compose exec -T postgres pg_isready -U scanner -d scannerdb; then
    echo "PASS: postgres is accepting connections"
else
    echo "FAIL: postgres is not accepting connections"
    docker-compose logs postgres
    docker-compose down
    exit 1
fi

echo ""
echo "Test 4: Checking redis connectivity on port 6379..."
if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
    echo "PASS: redis is responding to PING"
else
    echo "FAIL: redis is not responding to PING"
    docker-compose logs redis
    docker-compose down
    exit 1
fi

echo ""
echo "Test 5: Cleaning up with docker-compose down..."
docker-compose down

if [ $? -eq 0 ]; then
    echo "PASS: docker-compose down completed successfully"
else
    echo "FAIL: docker-compose down failed"
    exit 1
fi

echo ""
echo "=== All Tests Passed ==="
