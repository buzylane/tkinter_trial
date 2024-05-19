from setuptools import setup, find_packages

setup(
    name='Buzylane',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'psycopg2',  # Add other dependencies here
    ],
    entry_points={
        'console_scripts': [
            'your_command=your_script:main_function',
        ],
    },
    author='STANLEY',
    author_email='workbuzylane@gmail.com',
    description='This is a trial system',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/buzylane/tkinter_trial.git',
)
