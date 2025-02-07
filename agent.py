import time
from langgraph.checkpoint.memory import MemorySaver
from langgraph.func import entrypoint, task
from langgraph.types import interrupt, Command
from util import llm_call


@task
def write_essay(topic: str) -> str:
    """Write an essay about the given topic."""
    return llm_call(f"""
    Write an essay about topic: {topic}
    All essay should be written in Japanese.
    """)


@entrypoint(checkpointer=MemorySaver())
def workflow(topic: str) -> dict:
    """A simple workflow that writes an essay and asks for a review."""
    while True:
        essay = write_essay(topic).result()
        is_approved = interrupt(
            {
                # Any json-serializable payload provided to interrupt as argument.
                # It will be surfaced on the client side as an Interrupt when streaming data
                # from the workflow.
                "essay": essay,  # The essay we want reviewed.
                # We can add any additional information that we need.
                # For example, introduce a key called "action" with some instructions.
                "action": "approve/rejectを入力してください: ",
            }
        )

        if is_approved.lower() == "approve":
            break

    return {
        "essay": essay,  # The essay that was generated
        "is_approved": is_approved,  # Response from HIL
    }


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "some_thread_id"}}

    current_input = input("Enter a topic: ")
    # 初回はトピックを入力として使用

    while True:
        interrupt_detected = False
        # current_input（初回はトピック、以降はCommandオブジェクト）に対してstreamを開始
        for chunk in workflow.stream(current_input, config):
            print(chunk)
            # chunk内の各タスク結果をチェック
            for task_name, result in chunk.items():
                if task_name == "__interrupt__":
                    # interruptが発生した場合、ユーザーからの応答を受け取りCommandを生成する
                    resume = input(result[0].value["action"])
                    current_input = Command(resume=resume)
                    interrupt_detected = True
                    # 複数のinterruptが発生している場合、ここでbreakして外側のwhileループで再度streamを呼び出す
                    break
                elif task_name == "workflow":
                    # workflowが完了した場合は最終結果を出力して終了する
                    print("最終結果:")
                    print("承認状態:", result["is_approved"])
                    print("エッセイ内容:", result["essay"])
                    exit(0)
            if interrupt_detected:
                # interruptがあったので、現在のstreamループを終了し、新たな入力で再実行
                break

        if not interrupt_detected:
            # もしinterruptが一度も発生しなかったなら、streamの全出力が完了したと判断してループを抜ける
            break
