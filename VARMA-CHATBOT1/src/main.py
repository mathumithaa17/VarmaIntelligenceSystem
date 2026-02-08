from src.retriever import VarmaRetriever
from src.llm.prompt import build_prompt
from src.llm.generator import generate


def main():
    retriever = VarmaRetriever()

    print("🟢 Varma Chatbot (RAG + LLaMA)")
    print("Type 'exit' to quit\n")

    while True:
        query = input("User: ").strip()
        if query.lower() == "exit":
            break

        docs = retriever.retrieve(query)
        context = "\n\n".join([d["text"] for d in docs])

        prompt = build_prompt(query, context)
        response = generate(prompt)

        print("\n" + response + "\n")


if __name__ == "__main__":
    main()
