import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent.tools import pdf_parser


class PDFOwnershipTests(unittest.TestCase):
    def test_search_only_returns_requested_patients_documents(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            store = Path(temporary_dir)

            documents = [
                ("aaaaaaaa", "P001", "aspirin patient-one-only"),
                ("bbbbbbbb", "P002", "aspirin patient-two-only"),
            ]

            for pdf_id, patient_id, text in documents:
                index = {
                    "pdf_id": pdf_id,
                    "patient_id": patient_id,
                    "filename": f"{pdf_id}.pdf",
                    "chunks": [text],
                }
                (store / f"{pdf_id}_index.json").write_text(
                    json.dumps(index), encoding="utf-8"
                )

            with patch.object(
                pdf_parser, "PDF_UPLOAD_DIR", temporary_dir
            ):
                result = pdf_parser.search_pdf_content.invoke({
                    "query": "aspirin",
                    "patient_id": "P001",
                })

                self.assertIn("patient-one-only", result)
                self.assertNotIn("patient-two-only", result)

                # Knowing another patient's PDF ID must not bypass filtering.
                result = pdf_parser.search_pdf_content.invoke({
                    "query": "aspirin",
                    "patient_id": "P001",
                    "pdf_id": "bbbbbbbb",
                })

                self.assertNotIn("patient-two-only", result)
                self.assertEqual(
                    result,
                    "No matching content found in this patient's documents.",
                )


if __name__ == "__main__":
    unittest.main()