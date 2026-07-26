def clean_text(text):
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())
