"""Run the questions in test_questions.txt through Foxy."""

import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv


TABLE_HEADER = (
    "| Band | Question | Foxy's answer | Safe? | Correct? | "
    "Child-friendly? | Notes |\n"
    "| --- | --- | --- | --- | --- | --- | --- |\n"
)


def cell(value):
    """Keep text on one Markdown table row."""
    return str(value).replace("|", r"\|").replace("\r\n", "<br>").replace("\n", "<br>").replace("\r", "<br>")


def read_questions(path):
    questions = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "|" not in line:
            questions.append(("", line.strip(), "Invalid row: expected a band, |, and question."))
            continue
        band, question = line.split("|", 1)
        band, question = band.strip(), question.strip()
        if not band or not question:
            questions.append((band, question, "Invalid row: band and question are required."))
        else:
            questions.append((band, question, ""))
    return questions


def main():
    folder = Path(__file__).resolve().parent
    questions_path = folder / "test_questions.txt"
    results_path = folder / "test_run_results.md"

    try:
        questions = read_questions(questions_path)
    except OSError:
        print("I couldn't read test_questions.txt.")
        return

    load_dotenv(folder / ".env")
    provider = os.getenv("PROVIDER", "").strip().lower()
    model = os.getenv("MODEL", "").strip()
    api_key = os.getenv("API_KEY", "").strip()
    setup_error = ""
    system_prompt = ""
    client = None

    if provider != "anthropic":
        setup_error = "Please set PROVIDER=anthropic in .env."
    elif not model or not api_key:
        setup_error = "Please add MODEL and API_KEY to .env."
    else:
        try:
            system_prompt = (folder / "foxy_prompt.txt").read_text(encoding="utf-8")
            client = anthropic.Anthropic(api_key=api_key)
        except OSError:
            setup_error = "I couldn't read foxy_prompt.txt."
        except Exception:
            setup_error = "Foxy could not be initialized; check the provider settings."

    with results_path.open("w", encoding="utf-8", newline="") as results:
        results.write(TABLE_HEADER)
        total = len(questions)
        for index, (band, question, row_error) in enumerate(questions, 1):
            print(f"Running {index} of {total}...")
            answer = ""
            error = row_error or setup_error

            if not error:
                try:
                    reply = client.messages.create(
                        model=model,
                        max_tokens=1500,
                        system=f"{system_prompt}\n\nThe child's age band is {band}.",
                        messages=[{"role": "user", "content": question}],
                    )
                    text_blocks = [
                        block for block in reply.content
                        if getattr(block, "type", "") == "text"
                    ]
                    answer = "".join(block.text for block in text_blocks)
                    if not answer.strip():
                        answer = "I'm here with you. Can you tell me a little more?"
                except Exception:
                    error = "Request failed; check provider settings and connection."

            if error:
                answer = f"Error: {error}"
            results.write(
                f"| {cell(band)} | {cell(question)} | {cell(answer)} |  |  |  |  |\n"
            )

    print(f"Done. Results saved to {results_path.name}.")


if __name__ == "__main__":
    main()
