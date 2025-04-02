#!/bin/bash

# Set the path to your project
PROJECT_PATH="/path/to/your/project"

# Navigate to the project directory
cd $PROJECT_PATH

# Activate virtual environment if you're using one
# source /path/to/your/virtualenv/bin/activate

# Run the management command
python manage.py archive_old_jobs

# Log the execution
echo "$(date): Archived old jobs" >> $PROJECT_PATH/logs/cron.log 