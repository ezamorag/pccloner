from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pccloner',
    version='0.1.8',
    description= "Clone your repetitive PC tasks",
    py_modules = ['pccloner.pcdata', 'pccloner.pctask_press', 'pccloner.pctask_pr', 'pccloner.win11', 'pccloner.ubuntu', 'pccloner.utils'],
    packages = find_packages(),
    package_dir = {'':'src'},
    
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    
    install_requires = ['pynput >= 1.7.6',
                        'pyautogui >= 0.9.54',
                        'keyboard >= 0.13.5',
                        'pandas >= 2.1.4',
                        'py7zr >= 0.22.0',
                        'mss >= 9.0.2',
                       ],
    
    url="https://github.com/ezamorag/pccloner",
    author="Erik Zamora",
    author_email="ezamora1981@gmail.com",
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)

