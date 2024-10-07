import openai  # Assuming you have the OpenAI API key set up.
from openai import OpenAI
import os
import json
import re
from dotenv import load_dotenv
import argparse


from dotenv import load_dotenv
import os
from openai import OpenAI

# clean up imports
# next, we break this multiple GPTs to each do these pieces individually


# Load environment variables from the .env.local file
load_dotenv(".env.local")

# Retrieve the OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY1")

# Check if the API key was retrieved successfully
if not api_key:
    raise EnvironmentError(
        "OpenAI API key not found. Please ensure 'OPENAI_API_KEY1' is set in the .env.local file."
    )

# Create an OpenAI client instance using the retrieved API key
client = OpenAI(api_key=api_key)


def chunk_text(text, max_characters=500):
    """
    Helper function to chunk the transcript text into manageable segments.
    """
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in text.split(". "):
        sentence_length = len(sentence) + 2  # Account for the '. ' delimiter.
        if current_length + sentence_length > max_characters:
            # If adding this sentence exceeds max length, finalize the current chunk.
            chunks.append(". ".join(current_chunk) + ".")
            current_chunk = [sentence]
            current_length = sentence_length
        else:
            current_chunk.append(sentence)
            current_length += sentence_length

    # Append the last chunk if any.
    if current_chunk:
        chunks.append(". ".join(current_chunk) + ".")

    return chunks


def format_transcript_with_gpt1(chunk):
    """
    Function to send the chunked transcript to GPT for formatting.
    """
    # Define the prompt that instructs GPT to format the chunk.
    prompt = f"""
    Format the following transcript chunk into a clean and skimmable format. 

    Example format:
    **Speaker 1:**:
    - Sentence 1
    - Sentence 2.

    **Speaker 2:**:
    - Sentence 1.
    - Sentence 2.
    
    Transcript chunk:
    \"\"\"{chunk}\"\"\"
    """
    # Use ChatCompletion.create for GPT-3.5 or GPT-4 models
    response = client.chat.completions.create(
        model="gpt-4-0613",  # Replace with the correct model
        messages=[
            {"role": "system", "content": "You are a formatting assistant."},
            {
                "role": "system",
                "content": (
                    "Your task is to clean and format the transcript text according to the following rules, "
                    "and then provide a 'reasoning' key explaining how you adhered to each rule.\n\n"
                    "1. If a speaker has more than 4 sentences of text, break it up into smaller paragraphs.\n"
                    "2. Ensure chronological order is preserved, with no text from one speaker combined with the next speaker’s text.\n"
                    "3. Ensure all words from the original text are in the output text in the same chronological order. No new text will be added. \n"
                    "4. There will be no added symbols (hyphens, colons etc), other than one colon after identifying the speaker.\n"
                    "4. Do not add extra spacing between paragraphs beyond the regular space.\n\n"
                    "Here's an example of how the text should be formatted:\n\n"
                    "**David:** And your competitors would’ve caught up.\n\n"
                    "**Jensen:** Well, not to mention we would’ve been out of business.\n\n"
                    "**David:** Who cares?\n\n"
                    "**Jensen:** Exactly. If you’re going to be out of business anyway, that plan obviously wasn’t the plan.\n\n"
                    "The plan that companies normally go through—build a chip, write the software, fix the bugs, tape out a new chip, so on and so forth—that method wasn’t going to work.\n\n"
                    "The question is, if we only had six months and you get to tape out just one time, then obviously you’re going to tape out a perfect chip.\n\n"
                    "I remember having a conversation with our leaders and they said, but Jensen, how do you know it’s going to be perfect?\n\n"
                    "I said, I know it’s going to be perfect, because if it’s not, we’ll be out of business. So let’s make it perfect.\n\n"
                    "We get one shot.\n\n"
                    "We essentially virtually prototyped the chip by buying this emulator.\n\n"
                    "Dwight and the software team wrote our software, the entire stack, ran it on this emulator, and just sat in the lab waiting for Windows to paint.\n\n"
                    "**David:** It was like 60 seconds for a frame or something like that.\n\n"
                    "The formatted output should include the key 'reasoning' as a separate field. The structure should look like this:\n\n"
                    "{\n"
                    '  "formatted_text": <your formatted text>,\n'
                    '  "reasoning": "<Explanation of how you followed each rule>"\n'
                    "}"
                ),
            },
            {
                "role": "system",
                "content": "Ensure that every line of text from the chunk is accounted for and included.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1500,
        top_p=1,
        frequency_penalty=0.5,
        presence_penalty=0,
    )
    # Print the entire response object to see its structure
    print("Full response object:", response)

    # Correct way to access the formatted content from the response
    message_content = response.choices[0].message.content

    # Print the message content to verify extraction
    print("Message content:\n", message_content)

    # Extract 'formatted_text' and 'reasoning' fields using regex
    formatted_text_match = re.search(
        r'"formatted_text":\s*"([^"]+)"', message_content, re.DOTALL
    )
    reasoning_match = re.search(r'"reasoning":\s*"([^"]+)"', message_content, re.DOTALL)

    # Get the extracted values if the matches are found
    formatted_text = formatted_text_match.group(1) if formatted_text_match else ""
    reasoning = reasoning_match.group(1) if reasoning_match else ""

    # Print the extracted values for debugging
    print("Formatted Text:\n", formatted_text)
    print("Reasoning:\n", reasoning)

    return formatted_text


def gpt_html_formatting(formatted_text):
    """
    Step 2: Function to apply HTML formatting to the already formatted text.
    """
    # Use a custom delimiter to make HTML extraction easy.
    prompt = f"""
    Take the following formatted transcript text and convert it into HTML with proper tags and styling. Ensure the HTML is free from extra labels, nested code blocks, or Markdown formatting like ` ```html `. Wrap the HTML content between <!-- START HTML --> and <!-- END HTML --> for easy extraction. Use <b> tags to bold speaker names and <p> tags for paragraphs.
    Formatted text:
    \"\"\"{formatted_text}\"\"\"
    """

    response = client.chat.completions.create(
        model="gpt-4-0613",
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that converts formatted text into HTML.",
            },
            {"role": "user", "content": prompt},
        ],
    )

    # Extract the HTML content using the provided delimiters.
    content = response.choices[0].message.content.strip()
    start_index = content.find("<!-- START HTML -->") + len("<!-- START HTML -->")
    end_index = content.find("<!-- END HTML -->")
    html_content = content[start_index:end_index].strip()

    return html_content


def create_html_from_chunks(chunks, file_name):
    """
    Combine all formatted chunks into a cohesive HTML document.
    Include the file name as the HTML document's title.
    """
    # Define the updated style properties with padding, margin, and max-width.
    style = f"""
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Lora:wght@400&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Lora', sans-serif;
                font-style: normal;
                font-weight: 400;
                font-size: 22px;
                line-height: 33px;
                color: #333333;
                background-color: white;
                padding: 20px;
                margin: 0;
                max-width: 800px;
                margin-left: auto;
                margin-right: auto;
            }}
            p {{
                margin-bottom: 16px;
            }}
            b {{
                font-weight: bold;
            }}
        </style>
        <title>{file_name}</title> <!-- Set the file name as the title of the document -->
    </head>
    """

    # Initialize HTML content with styles.
    html_content = style + "<body>"

    # Use enumerate to get index and chunk correctly.
    # Use enumerate to get index and chunk correctly.
    for index, chunk in enumerate(chunks):
        # Step 1: Format the text for readability using GPT formatting function.
        formatted_text = format_transcript_with_gpt1(
            chunk
        )  # Call format_transcript_with_gpt first

        # Print to verify the formatted text content
        print(f"Formatted Text for Chunk {index + 1}:\n{formatted_text}")
        # Step 2: Convert the formatted text into HTML using gpt_html_formatting.
        formatted_html = gpt_html_formatting(formatted_text)

        # Add the formatted HTML to the final content.
        html_content += f"<p>{formatted_html}</p>"
    html_content += "</body>"
    return html_content


def main():
    # Set up argument parser to handle input text file or folder.
    parser = argparse.ArgumentParser(
        description="Process transcript text files and format them into HTML."
    )
    parser.add_argument(
        "input_paths",
        type=str,
        nargs="+",  # Accepts multiple input paths (file or folder)
        help="Paths to the input text file(s) or folder(s) containing text files.",
    )

    # Parse the command-line arguments.
    args = parser.parse_args()

    # Iterate over all input paths provided.
    for input_path in args.input_paths:
        if os.path.isfile(input_path):
            # If a single file is provided, process it.
            print(f"Processing file: {input_path}")
            process_transcript_file(input_path)
        elif os.path.isdir(input_path):
            # If a directory is provided, process all text files in the directory.
            print(f"Processing directory: {input_path}")
            text_files = list(Path(input_path).glob("*.txt"))
            if not text_files:
                print(f"No text files found in directory: {input_path}")
                continue
            for text_file in text_files:
                print(f"Processing file: {text_file}")
                process_transcript_file(text_file)
        else:
            print(
                f"Invalid input path: {input_path}. Please provide a valid file or folder path."
            )


# Run the main function if this script is executed directly.
if __name__ == "__main__":
    main()
