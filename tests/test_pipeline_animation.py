from html.parser import HTMLParser
from pathlib import Path
import unittest


class SourceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.external_sources = []

    def handle_starttag(self, tag, attributes):
        for name, value in attributes:
            if name == "src" and value and value.startswith(("http://", "https://")):
                self.external_sources.append(value)


class PipelineAnimationTest(unittest.TestCase):
    def test_animation_contains_offline_pipeline_contract(self):
        path = Path("demo/pipeline-animation.html")
        content = path.read_text()
        required_text = [
            "Trusted ADAS Release",
            "Vendor conversion + merge",
            "JSON parses",
            "Training loader accepts",
            "Class-map contract",
            "Geometry drift",
            "Image linkage",
            "Round-trip IoU",
            "Split leakage",
            "FAIL",
            "Play",
            "Pause",
            "Restart",
            "Step",
            "prefers-reduced-motion",
        ]

        for text in required_text:
            self.assertIn(text, content)

        parser = SourceParser()
        parser.feed(content)
        self.assertEqual(parser.external_sources, [])
