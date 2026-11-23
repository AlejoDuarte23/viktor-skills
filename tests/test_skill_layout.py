import re
import unittest
from pathlib import Path


SKILLS_DIR = Path(__file__).resolve().parents[1] / "skills"


class SkillLayoutTests(unittest.TestCase):
    def test_skills_use_installable_folder_names(self):
        skills = sorted(SKILLS_DIR.rglob("SKILL.md"))
        self.assertTrue(skills)
        for skill in skills:
            with self.subTest(skill=skill):
                self.assertEqual(skill.parent.parent, SKILLS_DIR)
                name = re.search(r"^name:\s*(\S+)\s*$", skill.read_text(), re.MULTILINE)
                self.assertIsNotNone(name)
                if name:
                    self.assertEqual(skill.parent.name, name.group(1))

    def test_relative_skill_references_exist(self):
        for markdown in SKILLS_DIR.rglob("*.md"):
            for reference in re.findall(r"`(\.\./[^`]+)`", markdown.read_text()):
                with self.subTest(file=markdown, reference=reference):
                    self.assertTrue((markdown.parent / reference).is_file())


if __name__ == "__main__":
    unittest.main()
