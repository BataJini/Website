#!/usr/bin/env python
import os
import sys
import subprocess
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobhub.settings')
django.setup()

# Current directory
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)

def run_command(command, cwd=None):
    """Run a shell command and print output"""
    print(f"Running: {command}")
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd or script_dir)
        while True:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                break
            if output:
                print(output.decode('utf-8').strip())
        
        return_code = process.poll()
        print(f"Command completed with return code: {return_code}")
        return return_code == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    """Run the job scraper and then import the jobs"""
    print("Starting automated job update...")
    
    # Step 1: Run the main.py scraper to collect job data
    print("\n--- STEP 1: Scraping jobs from NoFluffJobs ---")
    if not run_command("python main.py"):
        print("Error running job scraper. Exiting.")
        return False
    
    # Step 2: Import the jobs using the Django management command
    print("\n--- STEP 2: Importing jobs into the database ---")
    import_cmd = "python ../manage.py import_jobs --nofluff nofluff_data.json --desc desc_data.json --response nofluff_response.json"
    if not run_command(import_cmd):
        print("Error importing jobs. Check the error messages above.")
        return False
    
    print("\nJob update process completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 