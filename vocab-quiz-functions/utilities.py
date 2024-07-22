import sys
import os
import csv
from nltk.stem import PorterStemmer
import argparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

def validate_file_content():
    try:
        with open('data/VOCABULARY.csv', 'r') as file:
            rowno = 2
            skipfirst = True
            for line in file:
                # Loop over each row in the file
                if skipfirst:
                    skipfirst = False
                    continue
                row = line.replace('\n','').split(',')
                item = {}
                item['word'] = row[0]
                item['stem'] = row[1]
                rowno += 1
        print(f'File has {rowno - 1} vocabular entries.')
    except Exception as e:
        print(f'Error at line {line}:{e}')
    finally:
        return

if __name__ == "__main__":
    build_word_vocabulary()
    validate_file_content()
    
    

 