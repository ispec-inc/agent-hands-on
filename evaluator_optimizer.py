from util import extract_xml, llm_call


def generate(prompt: str, task: str, context: str = "") -> tuple[str, str]:
    """
    フィードバックに基づいて解決策を生成し、改善する。
    """
    # context がある場合は、prompt、context、タスク情報を連結する。ない場合は prompt とタスク情報を連結する。
    full_prompt = f"{prompt}\n{context}\nタスク: {task}" if context else f"{prompt}\nタスク: {task}"
    response = llm_call(full_prompt)
    thoughts = extract_xml(response, "thoughts")
    result = extract_xml(response, "response")

    print("\n=== 生成開始 ===")
    print(f"考察:\n{thoughts}\n")
    print(f"生成結果:\n{result}")
    print("=== 生成終了 ===\n")

    return thoughts, result


def evaluate(prompt: str, content: str, task: str) -> tuple[str, str]:
    """
    解決策が要件を満たしているかどうかを評価する。
    """
    full_prompt = f"{prompt}\n元のタスク: {task}\n評価対象の内容: {content}"
    response = llm_call(full_prompt)
    evaluation = extract_xml(response, "evaluation")
    feedback = extract_xml(response, "feedback")

    print("=== 評価開始 ===")
    print(f"評価結果: {evaluation}")
    print(f"フィードバック: {feedback}")
    print("=== 評価終了 ===\n")

    return evaluation, feedback


def loop(task: str, evaluator_prompt: str, generator_prompt: str) -> tuple[str, list[dict]]:
    """
    要件が満たされるまで、生成と評価を繰り返す。
    """
    memory = []
    chain_of_thought = []

    thoughts, result = generate(generator_prompt, task)
    memory.append(result)
    chain_of_thought.append({"thoughts": thoughts, "result": result})

    while True:
        evaluation, feedback = evaluate(evaluator_prompt, result, task)
        if evaluation == "PASS":
            return result, chain_of_thought

        # 過去の試行結果とフィードバックをコンテキストとして連結する
        context = "\n".join(["過去の試行結果:", *[f"- {m}" for m in memory], f"\nフィードバック: {feedback}"])

        thoughts, result = generate(generator_prompt, task, context)
        memory.append(result)
        chain_of_thought.append({"thoughts": thoughts, "result": result})


if __name__ == "__main__":
    evaluator_prompt = """
    以下のコード実装を次の観点から評価してください：
    1. コードの正確性
    2. 時間計算量
    3. コードスタイルとベストプラクティス

    あなたは評価のみを行い、タスクの解決を試みるべきではありません。
    すべての基準が満たされ、これ以上改善の提案がない場合のみ "PASS" と出力してください。
    以下のフォーマットで評価を簡潔に出力してください。

    <evaluation>PASS, NEEDS_IMPROVEMENT, or FAIL</evaluation>
    <feedback>
    改善が必要な点とその理由を記述してください。
    </feedback>
    """

    generator_prompt = """
    あなたの目標は、<user input>に基づいてタスクを完成させることです。
    前回の生成結果からフィードバックがあれば、それを反映して解決策を改善してください。

    以下のフォーマットで回答を簡潔に出力してください:

    <thoughts>
    [タスクに対する理解、フィードバックに基づく考察、そして改善方法]
    </thoughts>

    <response>
    [ここにコード実装を記述]
    </response>
    """

    task = """
    <user input>
    次の操作を持つスタックを実装してください:
    1. push(x)
    2. pop()
    3. getMin()
    すべての操作は O(1) である必要があります。
    </user input>
    """

    loop(task, evaluator_prompt, generator_prompt)
