from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
    """Кастомный пользователь платформы знакомств (K1)."""

    GENDER_CHOICES = [("M", "Мужской"), ("F", "Женский"), ("O", "Другой")]
    STATUS_CHOICES = [
        ("searching", "В поиске"),
        ("taken", "Занят"),
        ("friends", "Ищу друзей"),
    ]

    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name="Пол"
    )
    age = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(18)],
        verbose_name="Возраст",
    )
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
    hobbies = models.TextField(blank=True, verbose_name="Увлечения")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="searching",
        verbose_name="Статус",
    )
    bio = models.TextField(blank=True, verbose_name="О себе")

    class Meta:
        ordering = ["id"]  # стабильная пагинация ленты профилей
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
