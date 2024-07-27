# testing-template

Yes, you can create a "doppelgänger" repository that contains stubs for modules within the main repository, allowing you to dynamically modify the module search path for these stubs without altering the main repository. This approach ensures that the main repository remains untouched and you can manage stubs for both external and internal modules.

### Steps to Create and Use a Doppelgänger Repository for Stubs

1. **Clone the Main Repository:**
   - Clone the repository you want to work on.

2. **Create a Doppelgänger Repository for Stubs:**
   - Create a sibling repository that will contain stubs for the internal modules.

3. **Create Stub Implementations:**
   - Develop stub implementations for the internal modules in the doppelgänger repository.

4. **Modify Python’s Module Search Path Dynamically:**
   - Use an external script to modify the `sys.path` to include the doppelgänger repository and other stubs based on environment variables.

5. **Run the Application:**
   - Use the external script to run your Django application with the necessary paths configured.

### Detailed Example

#### Step 1: Clone the Main Repository

Clone the repository you want to work on:

```sh
git clone https://github.com/your_org/django_app.git
cd django_app
```

#### Step 2: Create a Doppelgänger Repository for Stubs

Create a sibling repository for the stubs:

```sh
cd ..
mkdir django_app_stubs
mkdir -p django_app_stubs/main_app
```

#### Step 3: Create Stub Implementations

Implement stubs that mimic the interface of the internal modules.

**Example Stub for `main_app` Module:**

```python
# django_app_stubs/main_app/some_module.py
class SomeInternalClass:
    def some_method(self):
        return "stubbed value from main_app"
```

#### Step 4: Modify Python’s Module Search Path Dynamically

Create an external script to set up the environment with the stubs.

**run_with_stubs.py:**

```python
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
```

Set the environment variable and run the script:

```sh
export USE_STUBS=true
python run_with_stubs.py
```

#### Step 5: Run the Application

By running `python run_with_stubs.py`, your application will use the stubs from both the stubs directory and the doppelgänger repository, allowing you to develop and test your code as if it were running in the real environment.

### Putting It All Together

1. **Project Structure:**

```
your_project/
├── django_app/
│   ├── manage.py
│   ├── settings.py
│   └── views.py
├── django_app_stubs/
│   ├── main_app/
│   │   └── some_module.py
├── stubs/
│   ├── repo_a/
│   │   └── module_a.py
│   └── repo_b/
│       └── module_b.py
└── run_with_stubs.py
```

2. **Run the Application with Stubs:**

Navigate to your project directory and run:

```sh
export USE_STUBS=true
python run_with_stubs.py
```

### Explanation

1. **Doppelgänger Repository:**
   - The `django_app_stubs` directory contains stubs for internal modules of the main repository. This ensures that the main repository remains untouched.

2. **Modify `sys.path`:**
   - The `run_with_stubs.py` script dynamically modifies the `sys.path` to include both the stubs directory and the doppelgänger repository if the `USE_STUBS` environment variable is set.

3. **External Script:**
   - By using an external script, you ensure that your main repository and its configuration remain unchanged. The script configures the environment to use the stubs, allowing you to run the application seamlessly.

### Conclusion

By creating a doppelgänger repository for stubs of internal modules and dynamically modifying the module search path, you can maintain a clean separation between your development setup and the main repository. This approach allows you to use stubs for both internal and external dependencies without altering the main repository, providing a flexible and maintainable development environment.
