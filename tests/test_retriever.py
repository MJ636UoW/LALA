import unittest
from lala.rag.retriever import HybridRetriever, QueryCategory

class TestRetriever(unittest.TestCase):
    def test_classify_query(self):
        retriever = HybridRetriever()
        self.assertEqual(retriever.classify_query("Explain MITRE ATT&CK technique T1003"), QueryCategory.MITRE)
        self.assertEqual(retriever.classify_query("Check YARA rule syntax for ransomware"), QueryCategory.YARA)
        self.assertEqual(retriever.classify_query("Sigma rule for powershell execution"), QueryCategory.SIGMA)

if __name__ == "__main__":
    unittest.main()
