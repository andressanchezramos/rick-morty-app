#!/bin/bash

# Stop and remove Docker containers
docker compose down

# Deactivate the virtual environment if active
if [[ "$VIRTUAL_ENV" != "" ]]; then
    deactivate
fi
