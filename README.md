# GPT Summarizer

A Python script to summarize the content of a VTT (Web Video Text Tracks) file using OpenAI's GPT-3 language model.

## Requirements

* Python 3.6 or higher
* `openai` library
* `tiktoken` library

## Installation

1. Clone this repository or download and extract the ZIP file.
2. Install the required libraries using `pip install -r requirements.txt`.
3. Set up your OpenAI API credentials as environmental variables on your operating system. You will need `OPENAI_ORG_ID` and `OPENAI_API_KEY`.

## Usage

1. Run the script using `python summarize_vtt.py [VTT_FILE]` where `[VTT_FILE]` is the path to the VTT file you want to summarize. If no file is provided, the script will attempt to find the newest VTT file in your Downloads folder.
2. The summary will be output to a text file in the same directory as the VTT file with the same name and a `.txt` extension.

### Customizations

The following constants can be customized at the top of the `summarize_vtt.py` file:

* `MODEL_NAME`: the name of the GPT-3 model to use (default is `"gpt-3.5-turbo"`).
* `SECTION_LENGTH`: the maximum length (in tokens) of each section of text passed to the GPT-3 model (default is `3000`).
* `OVERLAP`: the number of tokens of overlap between each section of text (default is `50`).

Additionally, you can add jargon replacement terms by creating a file called `jargon.txt` in the same directory as the script. Each line should contain two strings separated by a comma. The first string is the jargon term to replace, and the second string is the replacement.

## License

This project is licensed under the MIT License. See `LICENSE` for more information.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgments

* [OpenAI](https://openai.com/) for providing access to their GPT-3 language model.
* [tiktoken](https://github.com/openai/tiktoken) for providing a fast BPE tokenizer for use with OpenAI's models.
* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2) for providing the original README.md template.
