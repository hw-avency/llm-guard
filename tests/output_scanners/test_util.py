from llm_guard.output_scanners import util


def test_get_scanner_by_name_supports_emotion_detection(monkeypatch):
    created = object()

    def fake_emotion_detection(**kwargs):
        assert kwargs == {"threshold": 0.7}
        return created

    monkeypatch.setattr(util, "EmotionDetection", fake_emotion_detection)

    scanner = util.get_scanner_by_name("EmotionDetection", {"threshold": 0.7})

    assert scanner is created
