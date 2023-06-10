import os

PROJECT_PATH = os.getcwd()

while os.path.basename(PROJECT_PATH) != 'botAI':
    PROJECT_PATH = os.path.dirname(PROJECT_PATH)

