import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import generate_demo_data


class DemoChecks(unittest.TestCase):
    def test_sample_data_has_no_real_identifying_material(self):
        for name, paragraphs in generate_demo_data.POLICIES.items():
            contents = " ".join(paragraphs).lower()
            self.assertTrue(name.startswith("demo_"))
            for forbidden in ("real patient ssn", "actual facility address", "private employee id"):
                self.assertNotIn(forbidden, contents)

    def test_generation_is_8_documents_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(generate_demo_data, "ROOT", Path(folder)):
                files = generate_demo_data.generate()
                self.assertEqual(len(files), 8)
                for file in files:
                    self.assertTrue(file.read_text().startswith(generate_demo_data.BANNER))
                with self.assertRaises(FileExistsError):
                    generate_demo_data.generate()


if __name__ == "__main__":
    unittest.main()
