import unittest
from lala.rag.privacy import LocalRAGPrivacyEngine

class TestRAGPrivacy(unittest.TestCase):
    def test_privacy_rejection_of_cloud_vector_services(self):
        privacy = LocalRAGPrivacyEngine()
        self.assertFalse(privacy.validate_endpoint("https://pinecone.io/vector_db"))
        self.assertFalse(privacy.validate_endpoint("https://weaviate.cloud/api"))
        self.assertFalse(privacy.validate_endpoint("https://api.openai.com/v1/embeddings"))

if __name__ == "__main__":
    unittest.main()
