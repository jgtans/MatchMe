import base64

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User

from .models import ProfileReaction

PNG_1x1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
    "AAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


class ReactionTests(APITestCase):
    """K7: тесты системы лайк/дизлайк."""

    @classmethod
    def setUpTestData(cls):
        cls.alice = User.objects.create_user(
            "alice", password="pass12345", age=25, city="Москва", status="searching"
        )
        cls.bob = User.objects.create_user(
            "bob", password="pass12345", age=27, city="СПб", status="searching"
        )
        cls.carol = User.objects.create_user(
            "carol", password="pass12345", age=30, city="Москва", status="searching"
        )

    def test_anonymous_cannot_like(self):
        response = self.client.post(
            "/api/reactions/",
            {"to_user": self.bob.id, "is_like": True},
        )
        self.assertEqual(response.status_code, 401)

    def test_authenticated_can_like(self):
        self.client.force_authenticate(user=self.alice)
        response = self.client.post(
            "/api/reactions/",
            {"to_user": self.bob.id, "is_like": True},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ProfileReaction.objects.count(), 1)
        self.assertTrue(ProfileReaction.objects.get().is_like)

    def test_cannot_like_yourself(self):
        """K6: валидатор 'нельзя оценивать себя'."""
        self.client.force_authenticate(user=self.alice)
        response = self.client.post(
            "/api/reactions/",
            {"to_user": self.alice.id, "is_like": True},
        )
        self.assertEqual(response.status_code, 400)

    def test_cannot_like_same_user_twice(self):
        self.client.force_authenticate(user=self.alice)
        self.client.post("/api/reactions/", {"to_user": self.bob.id, "is_like": True})
        second = self.client.post(
            "/api/reactions/",
            {"to_user": self.bob.id, "is_like": False},
        )
        self.assertEqual(second.status_code, 400)
        self.assertEqual(ProfileReaction.objects.count(), 1)

    def test_dislike_works(self):
        self.client.force_authenticate(user=self.alice)
        response = self.client.post(
            "/api/reactions/",
            {"to_user": self.bob.id, "is_like": False},
        )
        self.assertEqual(response.status_code, 201)
        self.assertFalse(ProfileReaction.objects.get().is_like)

    def test_profile_list_shows_likes_count(self):
        """K5: likes_count приходит через аннотацию, без N+1."""
        self.client.force_authenticate(user=self.alice)
        self.client.post("/api/reactions/", {"to_user": self.bob.id, "is_like": True})
        self.client.force_authenticate(user=self.carol)
        self.client.post("/api/reactions/", {"to_user": self.bob.id, "is_like": True})

        self.client.force_authenticate(user=None)
        response = self.client.get("/api/profiles/")
        bob_data = next(p for p in response.data["results"] if p["username"] == "bob")
        self.assertEqual(bob_data["likes_count"], 2)

    def test_filter_by_age_range(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/profiles/?age_min=26&age_max=29")
        usernames = {p["username"] for p in response.data["results"]}
        self.assertEqual(usernames, {"bob"})

    def test_photo_deleted_from_disk_on_delete(self):
        """K4: при удалении записи файл удаляется с диска."""
        import os

        self.client.force_authenticate(user=self.alice)
        upload = self.client.post(
            "/api/photos/",
            {"image": SimpleUploadedFile("p.png", PNG_1x1, "image/png")},
            format="multipart",
        )
        self.assertEqual(upload.status_code, 201)
        photo = self.alice.photos.first()
        path = photo.image.path
        self.assertTrue(os.path.exists(path))
        self.client.delete(f"/api/photos/{photo.id}/")
        self.assertFalse(os.path.exists(path))

    def test_view_history_created_on_retrieve(self):
        """K3: при просмотре профиля сохраняется запись в истории."""
        self.client.force_authenticate(user=self.alice)
        self.client.get(f"/api/profiles/{self.bob.id}/")
        from .models import ViewHistory

        self.assertEqual(
            ViewHistory.objects.filter(viewer=self.alice, viewed=self.bob).count(),
            1,
        )
