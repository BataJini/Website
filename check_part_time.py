#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_board.settings')
django.setup()

from authentication.models import Job

def check_part_time_jobs():
    jobs = Job.objects.filter(title__icontains='part')
    print("\nJobs with 'part' in title:")
    for job in jobs:
        print(f"ID: {job.id}")
        print(f"Title: {job.title}")
        print(f"Type: {job.type}")
        print("-" * 50)

if __name__ == '__main__':
    check_part_time_jobs() 