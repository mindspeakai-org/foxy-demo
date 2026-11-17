"""A small terminal chat with Foxy."""

import os

import anthropic
from dotenv import load_dotenv


AGE_BANDS = {
    "A": "1-2",
    "B": "3-4",
    "C": "5-6",
    "D": "7-8",
    "E": "9-10",
}


def main():
    # Read settings from the local .env file.
    load_dotenv()
    provider = os.getenv("PROVIDER", "").strip().lower()
    model = os.getenv("MODEL", "").strip()
    api_key = os.getenv("API_KEY", "").strip()
    debug = os.getenv("DEBUG", "").strip().lower() == "true"

    if provider != "anthropic":
        print("Please set PROVIDER=anthropic in your .env file.")
        return
    if not model or not api_key:
        print("Please add MODEL and API_KEY to your .env file.")
        return

    # Read the system prompt without changing the file.
    try:
        with open("foxy_prompt.txt", "r", encoding="utf-8") as prompt_file:
            system_prompt = prompt_file.read()
    except OSError:
        print("I couldn't find foxy_prompt.txt. Please check that it is in this folder.")
        return

    print("Choose the child's age band:")
    for letter, ages in AGE_BANDS.items():
        print(f"{letter}: {ages}")

    while True:
        age_band = input("Age band (A-E): ").strip().upper()
        if age_band in AGE_BANDS:
            break
        print("Please choose A, B, C, D, or E.")

    system_prompt += f"\n\nThe child's age band is {age_band}."
    history = []
    client = anthropic.Anthropic(api_key=api_key)

    print('Foxy is ready! Type "quit" to leave.')
    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return

        if user_text.lower() == "quit":
            print("Goodbye!")
            return
        if not user_text:
            continue

        history.append({"role": "user", "content": user_text})
        try:
            reply = client.messages.create(
                model=model,
                max_tokens=1500,
                system=system_prompt,
                messages=history,
            )
        except Exception:
            # Keep provider details and secret settings out of the chat.
            print("Sorry, Foxy couldn't reply just now. Please check your settings and internet connection.")
            return

        text_blocks = [
            block for block in reply.content if getattr(block, "type", "") == "text"
        ]
        answer = "".join(block.text for block in text_blocks)
        if debug:
            print(f"Debug: stop_reason={reply.stop_reason!r}")
            print(f"Debug: content_blocks={len(reply.content)}")
            print(
                "Debug: block_types="
                f"{[getattr(block, 'type', 'unknown') for block in reply.content]!r}"
            )
            print(f"Debug: text={answer!r}")

        if not answer.strip():
            print("Foxy: I'm here with you. Can you tell me a little more?")
            continue

        history.append({"role": "assistant", "content": answer})
        print(f"Foxy: {answer}")


if __name__ == "__main__":
    main()
