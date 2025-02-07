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

sudo docker compose run --rm app sh -c "python manage.py startapp core"
sudo docker compose run --rm app sh -c "python manage.py makemigrations"


# Remove migration.
docker volume ls
docker volume rm recipe-app-api_dev-db-data
sudo docker volume rm recipe-app-api_dev-db-data
sudo docker compose run --rm app sh -c "python manage.py wait_for_db && python manage.py migrate"

sudo docker compose run --rm app sh -c "python manage.py createsuperuser"