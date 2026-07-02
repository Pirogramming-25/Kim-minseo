from django.test import TestCase
from django.urls import reverse

from .models import Review


class ReviewCrudTests(TestCase):
    def setUp(self):
        self.review = Review.objects.create(
            title="스파이더맨",
            release_year=2021,
            genre="Action",
            rating=4.5,
            running_time=148,
            review="재미있는 영화",
            director="존 왓츠",
            actor="톰 홀랜드",
        )

    def test_review_list_page_shows_review_summary(self):
        response = self.client.get(reverse("reviews:index"))

        self.assertContains(response, "스파이더맨")
        self.assertContains(response, "2021년")
        self.assertContains(response, "Action")
        self.assertContains(response, "4.5")

    def test_create_review_redirects_to_list(self):
        response = self.client.post(
            reverse("reviews:create"),
            {
                "title": "매트릭스",
                "release_year": 1999,
                "genre": "SF",
                "rating": 5.0,
                "running_time": 136,
                "review": "명작",
                "director": "워쇼스키",
                "actor": "키아누 리브스",
            },
        )

        self.assertRedirects(response, reverse("reviews:index"))
        self.assertTrue(Review.objects.filter(title="매트릭스").exists())

    def test_update_review_redirects_to_detail(self):
        response = self.client.post(
            reverse("reviews:update", kwargs={"pk": self.review.pk}),
            {
                "title": "스파이더맨 노 웨이 홈",
                "release_year": 2021,
                "genre": "Action",
                "rating": 4.0,
                "running_time": 148,
                "review": "수정한 리뷰",
                "director": "존 왓츠",
                "actor": "톰 홀랜드",
            },
        )

        self.assertRedirects(response, reverse("reviews:detail", kwargs={"pk": self.review.pk}))
        self.review.refresh_from_db()
        self.assertEqual(self.review.title, "스파이더맨 노 웨이 홈")

    def test_delete_review_redirects_to_list(self):
        response = self.client.post(reverse("reviews:delete", kwargs={"pk": self.review.pk}))

        self.assertRedirects(response, reverse("reviews:index"))
        self.assertFalse(Review.objects.filter(pk=self.review.pk).exists())
