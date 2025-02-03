from util import llm_call


def main():
    prompt = input("プロンプトを入力: ")
    print(llm_call(prompt))


if __name__ == "__main__":
    main()
