import os
import re
import sys
import argparse

import openai
import tiktoken

# Settings
PERSONA_PROMPT = "You are to act as an expert project manager."

SECTION_PROMPT = f"{PERSONA_PROMPT} Paraphrase each thought into bullet point statements. Do not include an intro or conclusion."
TOPIC_PROMPT = f"{PERSONA_PROMPT} Separate the following notes into sections by topic. Do not change the wording or order of notes."
SUMMARY_PROMPT = f"{PERSONA_PROMPT} Summarize the following meeting notes in Key Takeaways and Action Items. Key Takeaways and Action Items should not repeat each other."

TEMPERATURE = 0
OVERLAP = 50
SECTION_RESPONSE_MAX_TOKENS = 1024

# Set up OpenAI API credentials and model name
# You must set these as environmental variables on your OS or change 'None' below (less secure)
ORG_ID = os.getenv("OPENAI_ORG_ID", None)
API_KEY = os.getenv("OPENAI_API_KEY", None)
if ORG_ID is None or API_KEY is None:
    print("Error: OPENAI_ORG_ID and OPENAI_API_KEY environment variables must be set.")
    sys.exit(1)
openai.organization = ORG_ID
openai.api_key = API_KEY

# Only compatable with chat models like gpt-3.5-turbo
MODEL = "gpt-3.5-turbo"

# Get the encoding for the GPT-2 model for tokenizing text
enc = tiktoken.get_encoding("gpt2")


def get_input_text(input_file):
    try:
        with open(input_file, 'r') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: file '{input_file}' not found.")
        sys.exit(1)
    return text


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Process text file and create summaries using OpenAI.")
    parser.add_argument("input_file", help="The input text file to process.")
    parser.add_argument("-o", "--output_file", nargs="?",
                        help="The output file where the results will be saved. If omitted, the output file will be named the same as the input file, but appended with '_output' and always have a '.txt' extension.")
    parser.add_argument("-t", "--topics", nargs="?", const="prompt", default="prompt",
                        help="Sort notes by topic. Provide a comma-separated list of topics or use 'auto' to automatically generate topics. Default is 'prompt' which will ask for the list at runtime.")
    parser.add_argument("-s", "--summary", action="store_true",
                        help="Generate a summary of the notes.")
    return parser.parse_args()


def clean_input_text(text):
    # Remove timestamps
    text = re.sub(
        r'\d{2}:\d{2}:\d{2}.\d{3} --> \d{2}:\d{2}:\d{2}.\d{3}\n', '', text)
    # Remove blank lines
    text = '\n'.join([line for line in text.split('\n') if line.strip()])
    # Remove VTT tags
    text = re.sub(r'<v [^>]+>', '', text)
    text = re.sub(r'</v>', '', text)
    # Remove whitespace and new lines
    text = re.sub(r'\s+', ' ', text)
    return text


def replace_jargon(text):
    # Check if jargon.txt file exists
    if os.path.isfile('jargon.txt'):
        # Read jargon strings and replacements from file
        with open('jargon.txt', 'r') as f:
            jargon_pairs = [tuple(line.strip().split(','))
                            for line in f.readlines()]

            # Validate jargon pairs format
            for pair in jargon_pairs:
                if len(pair) != 2:
                    raise ValueError(
                        'Incorrect format in jargon.txt file. Each line should contain two strings separated by a comma.')

            # Replace jargon strings with their replacements in text
            for jargon, replacement in jargon_pairs:
                text = text.replace(jargon, replacement)
    else:
        print('jargon.txt file not found. Skipping jargon replacement...')

    return text


def process_sections(text):
    print(
        f"\nProcesing input text by section using the following prompt...\n\"{SECTION_PROMPT}\"\n")

    intro_text = f"{SECTION_PROMPT}###"
    outro_text = '###'

    n_sections = 0
    answers = []

    # Determine section length
    section_prompt_tokens = enc.encode(intro_text + outro_text)
    system_prompt = "You are a helpful assistant."
    system_prompt_tokens = enc.encode(system_prompt)
    tokenized_text = enc.encode(text)
    section_length = 4000 - SECTION_RESPONSE_MAX_TOKENS - \
        len(section_prompt_tokens) - len(system_prompt_tokens)

    for i in range(0, len(tokenized_text), section_length - OVERLAP):
        section_tokens = tokenized_text[i:i+section_length]
        section = enc.decode(section_tokens)
        section = intro_text + section + outro_text

        try:
            # Call the openai model with the section as input
            response = openai.ChatCompletion.create(
                model=MODEL,
                temperature=TEMPERATURE,
                max_tokens=SECTION_RESPONSE_MAX_TOKENS,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": section}
                ]
            )
        except openai.Error as e:
            print(
                f"Error: OpenAI API call failed with status code {e.status_code} and message: {e.message}")
            sys.exit(1)

        answer = response.choices[0].message.content

        # Filter out lines that don't start with "-" and are not blank
        filtered_lines = []
        for line in answer.split("\n"):
            line = line.strip()
            if line.startswith("-") or line:
                filtered_lines.append(line)
        filtered_answer = "\n".join(filtered_lines)

        answers.append(filtered_answer)
        print(filtered_answer)
        n_sections += 1

    # Combine the answers into a single string
    full_notes = '\n'.join(answers)
    return full_notes


def sort_by_topic(full_notes, topics):
    if topics is None:
        # Skip sorting notes
        return full_notes
    elif topics == "auto":
        # Let GPT pick the topics to sort by
        combined_topic_prompt = TOPIC_PROMPT
    else:
        # Use the specified topics to sort by
        combined_topic_prompt = f"{TOPIC_PROMPT} Topics: {topics}"

    print(
        f"\nSorting text by topic using the following prompt...\n\"{combined_topic_prompt}\"\n")

    topic_intro_text = f"{combined_topic_prompt}###"
    topic_outro_text = "###"

    # Determine max summary length
    topic_prompt_tokens = enc.encode(topic_intro_text + topic_outro_text)
    system_prompt = "You are a helpful assistant."
    system_prompt_tokens = enc.encode(system_prompt)
    full_notes_tokens = enc.encode(full_notes)
    topic_length = 4000 - len(full_notes_tokens) - \
        len(topic_prompt_tokens) - len(system_prompt_tokens)

    topic_input = topic_intro_text + full_notes + topic_outro_text

    try:
        # Call the openai model with the full_text_condensed as input
        response = openai.ChatCompletion.create(
            model=MODEL,
            temperature=TEMPERATURE,
            max_tokens=topic_length,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": topic_input}
            ]
        )
    except openai.Error as e:
        print(
            f"Error: OpenAI API call failed with status code {e.status_code} and message: {e.message}")
        sys.exit(1)

    sorted_notes = response.choices[0].message.content

    # Remove leading and trailing blank lines
    while sorted_notes.startswith("\n"):
        sorted_notes = sorted_notes[1:]
    while sorted_notes.endswith("\n"):
        sorted_notes = sorted_notes[:-1]

    print(f"{sorted_notes}")
    return sorted_notes


def process_summary(sorted_notes):
    print(
        f"\nSummarizing text using the following prompt...\n\"{SUMMARY_PROMPT}\"\n")
    summary_intro_text = f"{SUMMARY_PROMPT}###"
    summary_outro_text = '###'

    # Determine max summary length
    summary_prompt_tokens = enc.encode(summary_intro_text + summary_outro_text)
    tokenized_text = enc.encode(sorted_notes)
    system_prompt = "You are a helpful assistant."
    system_prompt_tokens = enc.encode(system_prompt)
    summary_length = 4000 - len(tokenized_text) - \
        len(summary_prompt_tokens) - len(system_prompt_tokens)

    summary_input = summary_intro_text + sorted_notes + summary_outro_text

    try:
        # Call the openai model with the full_text_condensed as input
        response = openai.ChatCompletion.create(
            model=MODEL,
            temperature=TEMPERATURE,
            max_tokens=summary_length,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": summary_input}
            ]
        )
    except openai.Error as e:
        print(
            f"Error: OpenAI API call failed with status code {e.status_code} and message: {e.message}")
        sys.exit(1)

    summary_notes = response.choices[0].message.content

    # Remove leading and trailing blank lines
    while summary_notes.startswith("\n"):
        summary_notes = summary_notes[1:]
    while summary_notes.endswith("\n"):
        summary_notes = summary_notes[:-1]

    print(f"{summary_notes}")
    return summary_notes


def write_output_to_file(input_file, output_file, combined_notes):
    if output_file is None:
        # Generate output file name from input file name
        input_file_base = os.path.splitext(input_file)[0]
        output_file = input_file_base + "_output.txt"

    try:
        with open(output_file, 'w') as f:
            f.write(combined_notes)
    except Exception as e:
        print(
            f"Error: could not write output to file {output_file}: {str(e)}")
        sys.exit(1)
    return output_file


def main():
    # Assign values based on user input
    args = parse_arguments()
    input_file = args.input_file
    output_file = args.output_file
    topics = args.topics
    generate_summary = args.summary

    # Prompt user for topics if needed
    if(topics == "prompt"):
        topics = input("What topics would you like to sort notes by? ")

    # Read input text from file
    input_text = get_input_text(input_file)

    # Process the input file and tokenize it
    clean_text = clean_input_text(input_text)
    clean_text = replace_jargon(clean_text)

    # Process sections of text
    full_notes = process_sections(clean_text)

    # Sort notes by topic (if requested)

    sorted_notes = sort_by_topic(full_notes, topics)

    # Summarize notes and combine with sorted_notes if requested
    if (generate_summary):
        summary_notes = process_summary(sorted_notes)

        # Combine summary and notes
        combined_notes = f"{summary_notes}\n\nNotes:\n{sorted_notes}"
    else:
        combined_notes = sorted_notes

    # Write to file
    output_file = write_output_to_file(input_file, output_file, combined_notes)

    print(f'\nYour summary of notes have been written to "{output_file}".')


if __name__ == "__main__":
    main()
