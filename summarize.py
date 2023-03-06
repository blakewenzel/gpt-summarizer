try:
    import os
    import sys
    import re
    import openai
    import tiktoken
except ModuleNotFoundError as e:
    missing_module = str(e).split("'")[1]
    print(
        f"Error: {missing_module} module not found. Please install it using 'pip install {missing_module}'")
    sys.exit(1)

# Settings
MODEL_NAME = "gpt-3.5-turbo"
SECTION_LENGTH = 3000
OVERLAP = 50

# Set up OpenAI API credentials and model name
# You must set these as environmental variables on your OS or change 'None' below (less secure)
ORG_ID = os.getenv("OPENAI_ORG_ID", None)
API_KEY = os.getenv("OPENAI_API_KEY", None)
if ORG_ID is None or API_KEY is None:
    print("Error: OPENAI_ORG_ID and OPENAI_API_KEY environment variables must be set.")
    sys.exit(1)
openai.organization = ORG_ID
openai.api_key = API_KEY

# Get the encoding for the GPT-2 model
enc = tiktoken.get_encoding("gpt2")

# Determine input file
if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
    input_file = sys.argv[1]
else:
    # If none passed in, find the newest .vtt file in the user's Downloads folder (should work on Mac,Windows,Linux)
    downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
    vtt_files = [f for f in os.listdir(downloads_dir) if f.endswith('.vtt')]
    if not vtt_files:
        print("Error: no VTT files found in Downloads folder.")
        sys.exit(1)
    input_file = max([os.path.join(downloads_dir, f)
                      for f in vtt_files], key=os.path.getctime)

try:
    with open(input_file, 'r') as f:
        text = f.read()
except FileNotFoundError:
    print(f"Error: file '{input_file}' not found.")
    sys.exit(1)


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


tokens = enc.encode(text)

print(f"File found! \"{input_file}\".\nProcessing summary...\n")

intro_text = 'You are an expert project manager. Summarize each thought into concise, succinct bullet point statements. No intro or conclusion needed.###'
outro_text = '###'

n_sections = 0
answers = []
total_tokens = 0

for i in range(0, len(tokens), SECTION_LENGTH - OVERLAP):
    section_tokens = tokens[i:i+SECTION_LENGTH]
    section = enc.decode(section_tokens)
    section = intro_text + section + outro_text

    try:
        # Call the openai model with the section as input
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": section}
            ]
        )
    except openai.Error as e:
        print(
            f"Error: OpenAI API call failed with status code {e.status_code} and message: {e.message}")
        sys.exit(1)

    total_tokens += response.usage.total_tokens
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
output_text = '\n'.join(answers)

# Write the output to a file
output_filename = os.path.join(downloads_dir, os.path.splitext(
    os.path.basename(input_file))[0] + '.txt')
try:
    with open(output_filename, 'w') as f:
        f.write(output_text)
except Exception as e:
    print(f"Error: could not write output to file {output_filename}: {str(e)}")
    sys.exit(1)

total_cost = round(total_tokens/1000*0.002, 3)

# Print summary of notes
print(
    f'\nYour summary of notes have been written to "{output_filename}" and used a total of {total_tokens} tokens for a total cost of ${total_cost}.')

# Ask the user if they want to delete the original .vtt file
delete_vtt_file = input(
    f"\nWould you like to keep the original .vtt file? (Y/n) ")
if delete_vtt_file.lower() == "n":
    try:
        os.remove(input_file)
        print(f"The original .vtt file has been deleted.")
    except Exception as e:
        print(f"Error: could not delete original file {input_file}: {str(e)}")
        sys.exit(1)
