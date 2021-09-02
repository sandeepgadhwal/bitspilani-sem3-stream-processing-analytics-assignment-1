#!/bin/bash
## Activate the environment, and run scrape:
#service cassandra start && \
cd /spaasgm && \
source ./miniconda/etc/profile.d/conda.sh && \
conda activate comappenv && \
./start-kafka.sh
#cd comapp && \
#python manage.py runserver 0.0.0.0:8000
