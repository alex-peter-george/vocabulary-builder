import sys
import os
import csv
from nltk.stem import PorterStemmer
import argparse

COMMAND = 'PREPDATA'

def in_venv_active():
    is_active = (sys.prefix != sys.base_prefix)
    print(is_active)
    return

def list_virtual_env():
    print(os.environ['VIRTUAL_ENV'])
    return

def build_word_vocabulary():
    data = [["WORD","STEM"]]
    with open('data/source_files/KINDLE_WORDS.csv', 'r') as file:
        # Create a CSV reader
        reader = csv.reader(file)
    
        # Loop over each row in the file
        skipfirst = True
        for row in reader:
            if skipfirst:
                skipfirst = False
                continue
            data.append([row[1],row[2]])

    with open('data/source_files/MY_WORDS.txt', 'r') as file:
        lines = file.readlines()
        ps = PorterStemmer()
        for line in lines:
            if len(line.strip().split(' ')) > 1:
                stem = 'N/A'
            else:
                stem = ps.stem(line.strip())
            data.append([line.strip().lower(),stem])

    # Open the file in write mode
    with open('data/VOCABULARY.csv', mode='w', newline='') as file:
        # Create a csv.writer object
        writer = csv.writer(file)
        # Write the data
        writer.writerows(data)

    print(f"CSV file ''data/VOCABULARY.csv'' created successfully.")
    return

if __name__ == "__main__":
    if (COMMAND == 'PREPDATA'):
        build_word_vocabulary()

    

 