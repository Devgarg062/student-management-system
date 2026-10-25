
import os
import tempfile
import unittest

import app as library_app


class LibraryTests(unittest.TestCase):

    def setUp(self):
        fd, self.temp_db = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        self.old_database = library_app.DATABASE
        library_app.DATABASE = self.temp_db
        library_app.init_db()

        self.client = library_app.app.test_client()

    def tearDown(self):
        # Close any remaining database connections before deleting the file.
        library_app.DATABASE = self.old_database

        if os.path.exists(self.temp_db):
            try:
                os.remove(self.temp_db)
            except PermissionError:
                pass

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")

    def test_add_book(self):
        response = self.client.post("/add", data={
            "title": "The Alchemist",
            "author": "Paulo Coelho",
            "category": "Fiction"
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.get("/")
        self.assertIn(b"The Alchemist", response.data)

    def test_missing_fields(self):
        response = self.client.post("/add", data={
            "title": "",
            "author": "Unknown",
            "category": "Fiction"
        })
        self.assertEqual(response.status_code, 400)

    def test_delete_book(self):
        self.client.post("/add", data={
            "title": "Test Book",
            "author": "Test Author",
            "category": "Testing"
        })

        with library_app.get_db() as conn:
            book = conn.execute(
                "SELECT id FROM books WHERE title = ?",
                ("Test Book",)
            ).fetchone()
            book_id = book["id"]

        response = self.client.post(f"/delete/{book_id}")
        self.assertEqual(response.status_code, 302)

        response = self.client.get("/")
        self.assertNotIn(b"Test Book", response.data)


if __name__ == "__main__":
    unittest.main()
