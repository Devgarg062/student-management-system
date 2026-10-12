
import unittest
import tempfile
import os

import app as student_app


class StudentManagementTests(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()

        self.old_db = student_app.DATABASE
        student_app.DATABASE = self.temp_db.name
        student_app.init_db()

        self.client = student_app.app.test_client()

    def tearDown(self):
        student_app.DATABASE = self.old_db
        os.unlink(self.temp_db.name)

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")

    def test_add_student(self):
        response = self.client.post("/add", data={
            "name": "Rahul",
            "email": "rahul@example.com",
            "course": "CSE"
        })

        self.assertEqual(response.status_code, 302)

        page = self.client.get("/")
        self.assertIn(b"Rahul", page.data)

    def test_missing_fields(self):
        response = self.client.post("/add", data={
            "name": "Rahul",
            "email": "",
            "course": "CSE"
        })

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
