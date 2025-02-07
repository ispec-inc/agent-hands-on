from util import llm_call


def chain(input: str, prompts: list[str]) -> str:
    result = input
    for i, prompt in enumerate(prompts):
        print(f"======\nStep {i + 1}: {prompt}\n======")
        result = llm_call(f"{prompt}\n Input: {result}")
        print(result)
    return result


if __name__ == "__main__":
    data_processing_steps = [
        """テキストから数値データと関連する指標のみを抽出する。
        各データを '値: 指標' の形式で新しい行に記載する。
        例:
        92: 顧客満足度
        45%: 収益成長""",
        """すべての数値データを可能な限りパーセント表記に変換する。
        パーセントやポイントでない場合は、小数に変換する（例: 92ポイント -> 92%）。
        各行に1つの数値を記載する。
        例:
        92%: 顧客満足度
        45%: 収益成長""",
        """すべての行を数値の降順で並べ替える。
        各行の形式は '値: 指標' を維持する。
        例:
        92%: 顧客満足度
        87%: 従業員満足度""",
        """並べ替えたデータを以下の形式のMarkdownテーブルとして整形する：
        | 指標 | 値 |
        |:--|--:|
        | 顧客満足度 | 92% |""",
    ]

    report = """
    Q3業績概要:
    今四半期の顧客満足度スコアは92ポイントに上昇しました。
    収益は前年比で45%成長しました。
    主要市場での市場シェアは23%になりました。
    顧客離脱率は8%から5%に減少しました。
    新規ユーザー獲得コストは1ユーザーあたり43ドルです。
    製品採用率は78%に増加しました。
    従業員満足度は87ポイントです。
    営業利益率は34%に改善しました。
    """

    print(chain(report, data_processing_steps))
