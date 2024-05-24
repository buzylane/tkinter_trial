import subprocess

def git_commit_and_push():
    try:
        # Staging changes
        subprocess.check_call(['git', 'add', '.'], cwd=r"C:\Users\workb\PycharmProjects\MultiplyHub\Beebi_Collections\TKINTER_TRIALS")
        print("Changes staged.")

        # Committing changes
        commit_message = "Update to application, added new features."
        subprocess.check_call(['git', 'commit', '-m', commit_message], cwd=r"C:\Users\workb\PycharmProjects\MultiplyHub\Beebi_Collections\TKINTER_TRIALS")
        print("Changes committed.")

        # Pushing changes
        subprocess.check_call(['git', 'push'], cwd=r"C:\Users\workb\PycharmProjects\MultiplyHub\Beebi_Collections\TKINTER_TRIALS")
        print("Changes pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

# Call the function to commit and push
git_commit_and_push()
