from pipeline import research_pipeline, ask_question


def main():
    
    topic = input("Enter a research topic: ")

    print("\nSearching, scraping, and storing articles...\n")
    research_pipeline(topic)

    print("Knowledge base is ready!\n")

    while True:
        question = input("Ask a question (or type 'exit' to quit): ")

        if question.lower() == "exit":
            print("Goodbye!")
            break

        answer = ask_question(question)

        print("\nAnswer:")
        print(answer)
        print("-" * 80)


if __name__ == "__main__":
    main()