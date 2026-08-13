from multilinguarag.language import detect_language


def test_detect_chinese():
    assert detect_language("检索增强生成可以连接外部知识库。") == "zh"


def test_detect_japanese():
    assert detect_language("検索拡張生成について説明します。") == "ja"


def test_detect_english():
    assert detect_language("Retrieval augmented generation uses external knowledge.") == "en"
