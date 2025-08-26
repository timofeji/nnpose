import platform
import sys
import os
import subprocess
import importlib
import pkg_resources
import venv
from typing import List, Optional, Dict

VENV_PATH='.venv'
pip_path = os.path.join(VENV_PATH, 'Scripts', 'pip.exe') if platform.system() == 'Windows' else os.path.join(VENV_PATH, 'bin', 'pip')
py_path = os.path.join(VENV_PATH, 'Scripts', 'python.exe') if platform.system() == 'Windows' else os.path.join(VENV_PATH, 'bin', 'python')
requirements_path = 'requirements.txt'

def check_dependencies(requirements_path: str = 'requirements.txt') -> Dict[str, bool]:

    if not os.path.exists(requirements_path):
        print(f"No requirements file found at {requirements_path}")
        return {}

    missing_deps = {}
    
    try:
        with open(requirements_path, 'r') as f:
            for line in f:
                # Skip comments and empty lines
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Parse package name (handling various requirement formats)
                try:
                    req = pkg_resources.Requirement.parse(line)
                    package_name = req.name
                except Exception:
                    # Fallback to simple parsing
                    package_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('!=')[0]
                
                try:
                    importlib.import_module(package_name.lower().replace('-', '_'))
                    missing_deps[package_name] = True
                except ImportError:
                    missing_deps[package_name] = False
    
    except Exception as e:
        print(f"Error checking dependencies: {e}")
        return {}
    
    return missing_deps

def run_setup() -> bool:
    # Create virtual environment
    if not os.path.exists(VENV_PATH):
        print(f"Creating virtual environment at {VENV_PATH}...")
        venv.create(VENV_PATH, with_pip=True)

    # Check and install dependencies
    print(f"Checking dependencies in {VENV_PATH}...")
    missing_deps = check_dependencies(requirements_path)
    if(missing_deps):
        print("Missing dependencies found:")
        for dep, installed in missing_deps.items():
            if not installed:
                print(f" - {dep} is not installed.")
        print("Installing missing dependencies...")
        subprocess.run(f'{pip_path} install -r {requirements_path}', check=True)
    
    return True 



def run(cfg):
    if(cfg.setup): 
        setup_success = run_setup()
        if not setup_success:
            print("Failed to set up the project environment.")
            sys.exit(1)

    if(cfg.config == "eval"):
        try:
            import eval
            eval.main(cfg)
        except ImportError as e:
            print(f"Error importing eval module: {e}")
            sys.exit(1)


import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default="default", help='configuration to run the application with')
    parser.add_argument('-setup', action="store_true", help='install dependencies and setup the project environment')
    parser.add_argument('-eval', action="store_true", help='run evaluation script')
    parser.add_argument('-train', action="store_true", help='run training script')
    parser.set_defaults()
    cfg = parser.parse_args()
    run(cfg)