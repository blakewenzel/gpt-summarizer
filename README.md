# GPT Summarizer

A Python script that utilizes OpenAI's GPT-3.5-turbo model to process and summarize text files.

## Features
* Paraprhases input text into bullet point statements.
* Sorts notes by specified topics or auto-generate topics.
* Summarizes text files into key takeaways and action items.
* Replaces jargon using a custom list. Useful for replacing incorrectly transcribed words or names.
* Supports VTT (Web Video Text Tracks) files.
* Optimizes input text to remove blank lines, whitespace, VTT tags, and timestamps before feeding into OpenAI to reduce costs.
* Supports long form text, such as from meeting transcripts. Will automatically separate input text into sections to be processed OpenAI in batches.

## Requirements

* Python 3.6 or higher
* `openai` library
* `tiktoken` library

## Installation

1. Clone this repository or download and extract the ZIP file.
2. Install the required libraries using `pip install -r requirements.txt`.
3. Set up your OpenAI API credentials as environmental variables on your operating system. You will need `OPENAI_ORG_ID` and `OPENAI_API_KEY`.

## Usage
```
python summarize.py [-h] [-o [OUTPUT_FILE]] [-t [TOPICS]] [-s] input_file
```

`input_file` is the path to the text file you want to summarize.

The summary will be output to a text file in the same directory as the input file with the same name appended with `_output.txt` unless the output file option is used.

### Options
```
  -h, --help            show this help message and exit
  -o [OUTPUT_FILE], --output_file [OUTPUT_FILE]
                        The output file where the results will be saved.
  -t [TOPICS], --topics [TOPICS]
                        Sort notes by topic. Provide a comma-separated list of topics or use 'auto' to automatically generate topics.
  -s, --summary         Generate a summary of the notes to be included in the output file.

```


### Jargon Replacement

You can add jargon replacement terms by creating a file called `jargon.txt` in the same directory as the script. Each line should contain two strings separated by a comma. The first string is the jargon term to replace, and the second string is the replacement.

## License

This project is licensed under the MIT License. See `LICENSE` for more information.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgments

* [OpenAI](https://openai.com/) for providing access to their GPT-3 language model.
* [tiktoken](https://github.com/openai/tiktoken) for providing a fast BPE tokenizer for use with OpenAI's models.
* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2) for providing the original README.md template.
