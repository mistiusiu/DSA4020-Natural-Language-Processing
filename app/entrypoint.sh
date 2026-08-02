#!/bin/bash

set -e


echo "Starting Translation API"



MODEL_DIR="/app/backend/models/facebook_nllb_1_3b"



if [ ! -d "$MODEL_DIR" ]; then

    echo "NLLB model not found."

    echo "Downloading NLLB-200..."

    python manage.py download_nllb

else

    echo "NLLB model already exists."

fi



echo "Running migrations..."

python manage.py makemigrations
python manage.py migrate



echo "Collecting static files..."

python manage.py collectstatic \
    --noinput || true


echo "Warming up translation model..."

python manage.py warmup_model


echo "Starting server..."

exec "$@"
