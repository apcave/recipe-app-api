#!/bin/bash


sudo docker build .
sudo docker compose build

# Linting with flake8
sudo docker compose run --rm app sh -c "flake8 ."

# Run tests
sudo docker compose run --rm app sh -c "python manage.py test"


sudo docker compose run --rm app sh -c "python manage.py collectstatic"


# Get CLI
sudo docker compose run --rm app sh

# Create a new Django project.
# sudo docker-compose run --rm app sh -c "django-admin startproject app ."


# Starts the web service
sudo docker compose up