import pytest

from app.parser import SummaryParseError, parse_summary


def test_parse_summary_stops_at_next_heading() -> None:
    html = """
    <div class="mw-parser-output">
      <h2><span id="Reborn">\"Reborn\"</span></h2>
      <h2><span id="Information">Information</span></h2>
      <p>Metadata that must not appear.</p>
      <h2><span id="Summary">Summary</span></h2>
      <p>First summary paragraph.</p>
      <figure><figcaption>An image caption.</figcaption></figure>
      <p>Second <b>summary</b> paragraph.</p>
      <h2><span id="Characters_in_Order_of_Appearance">Characters in Order of Appearance</span></h2>
      <p>This must not appear.</p>
    </div>
    """

    parsed = parse_summary(html, 1)

    assert parsed.title == "Reborn"
    assert parsed.paragraphs == [
        "First summary paragraph.",
        "Second summary paragraph.",
    ]


def test_parse_summary_raises_when_missing() -> None:
    with pytest.raises(SummaryParseError):
        parse_summary("<h2>Information</h2><p>No summary here.</p>", 12)
