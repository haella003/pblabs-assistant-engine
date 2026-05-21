import unittest
import os
import sys

# Steps backward out of server/tests/ so Python can see your application
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

class TestEDIBackend(unittest.TestCase):

    def test_persona_directory_exists(self):
        """Verify that the required system personas folder is in place."""
        personas_path = os.path.join("server", "personas")
        self.assertTrue(os.path.exists(personas_path), f"Expected folder missing at: {personas_path}")

    def test_knowledge_vault_directory_exists(self):
        """Verify that the vector store knowledge base folder exists."""
        vault_path = os.path.join("server", "knowledge_vault")
        self.assertTrue(os.path.exists(vault_path), f"Expected folder missing at: {vault_path}")

    def test_prompt_template_placeholder_checks(self):
        """Verify the structural tokens of your prompt template."""
        template_file = os.path.join("server", "personas", "prompt_template.txt")
        if os.path.exists(template_file):
            with open(template_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("{{persona}}", content, "Prompt blueprint is missing the {{persona}} token slot.")
            self.assertIn("{{retrieved_context}}", content, "Prompt blueprint is missing the vector context token slot.")

if __name__ == "__main__":
    unittest.main()