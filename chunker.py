# chunker.py

import re  # Import the regular expression module.
from text_formatter import (
    format_transcript_with_gpt,
)  # Import a function from text_formatter.py if required.


# Your existing chunk_text function
def chunk_text(text, max_characters=1500):
    """
    Helper function to chunk the transcript text into manageable segments.
    Ensures that the original word count is preserved.
    """
    chunks = []
    current_chunk = []
    current_length = 0

    # Split the text into sentences using a regex to preserve delimiters and avoid unintended spaces.
    sentences = re.split(r"(?<=[.!?]) +", text.strip())  # Fixing the NameError

    for sentence in sentences:
        sentence_length = len(sentence) + 1  # Include space or delimiter.

        if current_length + sentence_length > max_characters:
            # Finalize the current chunk when it exceeds the max length.
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_length = len(sentence)
        else:
            current_chunk.append(sentence)
            current_length += sentence_length

    # Append the last chunk if it exists.
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


# Test function to validate chunk_text
def test_chunk_text():
    input_text = """
    Lex: Talking about exciting things for an engineer, the same Snapdragon that goes to a phone and it can go to a galaxy phone, for example, Samsung, the same, not a special one, went all the way to Mars. You expect to have a full day of battery life, but then you want it to not be sending data into 10 or 100 megabits. You want gigabits. You want it to be able to have eight core processors. You want to have a GPU with ray tracing. You want to have all of the things that you can only get into, sometimes, a desktop PC to do all of that in your phone is an incredible thing.
    Cristiano: The following is a conversation with Cristiano Aman, the CEO of Qualcomm, the company that's one of the leaders in the world in the space of mobile communication and computation that connects billions of phones and the Snapdragon processor and system on a chip that is the brain of most of the premium Android phones in the world. This is a Lex Fridman podcast to support it, please check out our sponsors in the description.
    Lex: And now, dear friends, here's Cristiano Aman. You are originally from Brazil. So let me ask the most important question, the most profound question, the biggest question, who's the greatest football soccer player of all time? Look, everybody's going to say Pele. And actually, I was born at the during the game of Brazil and Italy, the Pele gave Brazil the championship. Actually, it was. My dad tells me that the doctor had a TV on at the delivery room.
    Cristiano: But so everybody will say Pele. But I really like Ronaldo, the first, the first Ronaldo. I really like him. That's my favorite player.
    Lex: Oh, the first Ronaldo. I really like him too. That's my favorite player.
    """

    # Calculate the word count of the original input text.
    original_word_count = len(input_text.split())

    # Use the chunk_text function to chunk the text.
    chunks = chunk_text(input_text, max_characters=500)

    # Calculate the total word count from all chunks.
    chunked_word_count = sum(len(chunk.split()) for chunk in chunks)

    print(f"Original word count: {original_word_count}")
    print(f"Chunked total word count: {chunked_word_count}")
    print(f"Number of chunks: {len(chunks)}")

    # Check if the word counts match.
    assert original_word_count == chunked_word_count, "Word counts do not match!"

    # Return the chunked outputs for verification.
    return chunks


# Main function to run the test or chunk_text function
def main():
    # Call the test function to verify chunking.
    chunks = test_chunk_text()
    print("\nChunks created from input text:\n")
    for i, chunk in enumerate(chunks, start=1):
        print(f"Chunk {i}:\n{chunk}\n")


if __name__ == "__main__":
    main()
