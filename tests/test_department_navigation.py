"""Entry-point routing remains complete in a checkout or source ZIP."""
import unittest
from tools.audit_departments import audit

class DepartmentNavigationTests(unittest.TestCase):
    def test_all_packaged_paths_have_a_department(self):
        result=audit()
        self.assertEqual(result['unmapped_paths'],0)
        self.assertEqual(result['file_moves'],0)
        self.assertEqual(len(result['departments']),7)

if __name__=='__main__':unittest.main()
