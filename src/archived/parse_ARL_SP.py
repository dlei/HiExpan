'''
__author__: Jiaming Shen
__description__: Parse the **text field** in Signal Processing corpus. The original XML input is transformed by Keqian
'''
import os, re
import utility

def main():
    inputFilePath = "../data/SignalProcessing/output_pureText.txt"
    outputFilePath = "../data/SignalProcessing/output_pureText_cleaned.txt"
    with open(inputFilePath, "r") as fin, \
        open(outputFilePath, "w") as fout:
        for line in fin:
            line = line.strip()
            line = re.sub(r'[^\x00-\x7F]+', ' ', line)
            # title and abstract as currently seperated using 5 spaces, replace them with ". "
            line = re.sub(r"\s{5}",". ", line)
            line = re.sub('\s+', ' ', line).strip()
            fout.write(line)
            fout.write("\n")


if __name__ == '__main__':
    main()
