import os
import sys
from pathlib import Path

# Check if the USE_STUBS environment variable is set
use_stubs = os.getenv('USE_STUBS', 'false') == 'true'

if use_stubs:
    # Calculate the path to the stubs directory
    current_dir = Path(__file__).resolve().parent
    stubs_path = current_dir / 'stubs'
    doppelganger_path = current_dir / 'django_app_stubs'

    # Add the stubs directory and doppelganger directory to the system path
    sys.path.insert(0, str(stubs_path))
    sys.path.insert(0, str(doppelganger_path))

# Add the main Django app directory to the system path
django_app_path = current_dir / 'django_app'
sys.path.insert(0, str(django_app_path))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')

# Run the Django development server
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    execute_from_command_line(['manage.py', 'runserver'])
