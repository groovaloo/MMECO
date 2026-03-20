#!/bin/bash
# Keep-alive script to prevent GitHub connection timeout
# Pings GitHub every minute to maintain connection

echo "Starting GitHub keep-alive service..."
echo "Pinging github.com every 60 seconds..."

while true; do
  # Ping GitHub to keep connection alive
  curl -I https://github.com > /dev/null 2>&1
  
  # Check if curl command was successful
  if [ $? -eq 0 ]; then
    echo "$(date): GitHub connection alive"
  else
    echo "$(date): GitHub connection check failed"
  fi
  
  # Wait for 60 seconds before next ping
  sleep 60
done