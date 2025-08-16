# ruff: noqa: E501
from django.test import TestCase
from core.templatetags.highlight_code import highlight_code


FAKE_PLAIN_TEXT_NAME = 'fake_file.barbaz'
FAKE_PLAIN_TEXT_CONTENT = """\
This is a fake text content for testing purposes.
"""

FAKE_PYTHON_NAME = 'fake_file.py'
FAKE_PYTHON_CONTENT = """\
def fake_function():
    print("This is a fake Python function.")
"""
FAKE_PYTHON_RESULT = """\
<div class="highlight"><pre><span></span><span class="linenos">1</span><span class="pygments-k">def</span><span class="pygments-w"> </span><span class="pygments-nf">fake_function</span><span class="pygments-p">():</span>\n<span class="linenos">2</span>    <span class="pygments-nb">print</span><span class="pygments-p">(</span><span class="pygments-s2">&quot;This is a fake Python function.&quot;</span><span class="pygments-p">)</span>\n</pre></div>
"""


class HighlightCodeTestCase(TestCase):
    def test_python_highlighting(self):
        # Test that Python code gets highlighted with pygments classes
        result = highlight_code(FAKE_PYTHON_CONTENT, FAKE_PYTHON_NAME)
        self.assertTrue(result.startswith('<div class="highlight">') and result.endswith('</div>\n'))
        self.assertTrue(FAKE_PYTHON_RESULT == result)

    def test_unknown_extension_fallback(self):
        result = highlight_code(FAKE_PLAIN_TEXT_CONTENT, FAKE_PLAIN_TEXT_NAME)
        self.assertTrue(result.startswith('<pre>') and result.endswith('</pre>'))
        self.assertTrue(FAKE_PLAIN_TEXT_CONTENT in result)

    def test_empty_content(self):
        result = highlight_code('', 'FAKE_PLAIN_TEXT_NAME')
        self.assertTrue(result.startswith('<pre></pre>'))
        self.assertTrue(len(result) == 11)

        result = highlight_code(None, 'FAKE_PLAIN_TEXT_NAME')
        self.assertTrue(result.startswith('<pre></pre>'))
        self.assertTrue(len(result) == 11)

    def test_empty_filename(self):
        result = highlight_code(' ', '')
        self.assertTrue(result.startswith('<pre> </pre>'))
        self.assertTrue(len(result) == 12)

        result = highlight_code(' ', None)
        self.assertTrue(result.startswith('<pre> </pre>'))
        self.assertTrue(len(result) == 12)
