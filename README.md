# GPT Summarizer

A Python script that utilizes OpenAI's GPT-3.5-turbo model to process and summarize long-form text files.

## Features
* Paraphrases input text into bullet point statements
* Sorts notes by specified topics or auto-generates topics
* Summarizes text files into key takeaways and action items
* Replaces specified terms using a custom jargon.txt file; useful for replacing repetitive transcription errors
* Supports text files, including VTT (Web Video Text Tracks) files
* Optimizes input text to remove blank lines, whitespace, VTT tags, and timestamps before feeding into OpenAI to reduce costs
* Supports long-form text, such as meeting transcripts; automatically separates input text into sections to be processed by OpenAI in batches that will not exceed the model's token limit


## Requirements

* Python 3.6 or higher
* `openai` library
* `tiktoken` library

## Installation

1. Clone this repository (or download and extract the ZIP file).
```shell
$ git clone https://github.com/blakewenzel/gpt-summarizer.git
```

2. Install the required libraries
```shell
$ pip install -r requirements.txt
```

3. Set up your OpenAI API credentials as environmental variables on your operating system. You will need `OPENAI_ORG_ID` and `OPENAI_API_KEY`.
```shell
$ export OPENAI_ORG_ID=YOUR_ORG_ID_HERE
$ export OPENAI_API_KEY=YOUR_API_KEY_HERE
```

## Usage
```shell
$ python summarize.py input_file
```

`input_file` is the path to the text file you want to summarize.

The summary will be output to a text file in the same directory as the input file with the same name appended with `_output.txt` unless the output file option is used.

### Options
```shell
$ python summarize.py [-h] [-o [OUTPUT_FILE]] [-j [JARGON_FILE]] [-t [TOPICS]] [-s] input_file
```

```shell
  -h, --help            show this help message and exit
  -o [OUTPUT_FILE], --output_file [OUTPUT_FILE]
                        The output file where the results will be saved. If omitted, the output file will be named the same as the input file, but appended with '_output' and always have a '.txt' extension.
  -j [JARGON_FILE], --jargon_file [JARGON_FILE]
                        Replace jargon terms before processing text. Will check for jargon.txt in the current working directory unless another file location is specified.
  -t [TOPICS], --topics [TOPICS]
                        Sort notes by topic. Provide a comma-separated list of topics or use 'auto' to automatically generate topics. Default is 'prompt' which will ask for the list at runtime.
  -s, --summary         Generate a summary of the notes.
```


### Jargon Replacement

You can have jargon terms replaced by creating a file called `jargon.txt` in the same directory as where the script is being run and using the `-j` option. Each line should contain two strings separated by a comma. The first string is the jargon term to replace, and the second string is the replacement.

Example `jargon.txt`:
```txt
AI,Artificial Intelligence
ML,Machine Learning
Sean,Shawn
Sarah,Sara
```
