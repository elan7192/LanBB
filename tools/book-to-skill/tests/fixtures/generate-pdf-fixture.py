#!/usr/bin/env python3
"""Write tests/fixtures/widget-protocol.pdf — synthetic public-domain sample.

One page of extractable text (Helvetica). Regenerate with:
  python3 tools/book-to-skill/tests/fixtures/generate-pdf-fixture.py
"""

from __future__ import annotations

from pathlib import Path

# Minimal valid PDF 1.4 with text layer (not image-only). Same content as
# widget-protocol.md, shortened for a single page.
_PDF = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 220 >>
stream
BT
/F1 16 Tf
72 720 Td
(Widget Protocol Handbook) Tj
0 -28 Td
(Chapter 1 Handshake) Tj
0 -20 Td
(Use the three-way handshake when opening a stream.) Tj
0 -28 Td
(Chapter 2 Backpressure) Tj
0 -20 Td
(Prefer credit-based flow control over unbounded queues.) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
0000000538 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
617
%%EOF
"""


def main() -> None:
    out = Path(__file__).resolve().parent / "widget-protocol.pdf"
    out.write_bytes(_PDF)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
