import subprocess
import os

def update_script():
    try:
        # Change directory to the script's directory
        script_dir = os.path.dirname(os.path.realpath(__file__))
        os.chdir(script_dir)

        # Pull the latest changes from the repository
        subprocess.check_call(['git', 'pull'])
        print("Successfully updated the script from GitHub repository.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to update the script. Error: {e}")

# Call the update function at the beginning
update_script()
