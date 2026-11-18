import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from memory import patient_memory


class PatientDirectoryTests(unittest.TestCase):
    def test_valid_id_creates_directory_inside_storage(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            with patch.object(
                patient_memory, "PATIENT_MEMORY_DIR", temporary_dir
            ):
                result = patient_memory._patient_dir("P001")

                self.assertEqual(
                    result, Path(temporary_dir).resolve() / "P001"
                )
                self.assertTrue(result.is_dir())

    def test_invalid_ids_are_rejected_without_creating_files(self):
        invalid_ids = [
            "",
            "../other-patient",
            r"..\other-patient",
            "/absolute",
            r"C:\other-patient",
            "patient/name",
            "patient name",
            "CON",
            "nul",
            "a" * 65,
            None,
        ]

        with tempfile.TemporaryDirectory() as temporary_dir:
            with patch.object(
                patient_memory, "PATIENT_MEMORY_DIR", temporary_dir
            ):
                for patient_id in invalid_ids:
                    with self.subTest(patient_id=patient_id):
                        with self.assertRaises(ValueError):
                            patient_memory._patient_dir(patient_id)

                self.assertEqual(
                    list(Path(temporary_dir).iterdir()), []
                )


if __name__ == "__main__":
    unittest.main()