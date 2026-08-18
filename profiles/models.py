from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from users.models import User


class ProfilePhoto(models.Model):
    """Фотография профиля. Одна из них — главная (K4: удаление с диска)."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name="Пользователь",
    )
    image = models.ImageField(upload_to="photos/", verbose_name="Фото")
    is_main = models.BooleanField(default=False, verbose_name="Главное фото")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_main", "-uploaded_at"]
        verbose_name = "Фото профиля"
        verbose_name_plural = "Фото профиля"

    def __str__(self):
        return f"Фото {self.user.username}{' (главное)' if self.is_main else ''}"

    def clean(self):
        """Гарантируем: только одно главное фото на пользователя."""
        super().clean()
        if self.is_main:
            existing_main = (
                ProfilePhoto.objects.filter(user=self.user, is_main=True)
                .exclude(pk=self.pk)
                .exists()
            )
            if existing_main:
                raise ValidationError(
                    "У пользователя уже есть главное фото — снимите флаг с другого."
                )

    def save(self, *args, **kwargs):
        """Если это первое фото пользователя — делаем его главным автоматически."""
        if not self.pk and not ProfilePhoto.objects.filter(user=self.user).exists():
            self.is_main = True
        super().save(*args, **kwargs)


@receiver(post_delete, sender=ProfilePhoto)
def delete_photo_from_disk(sender, instance, **kwargs):
    """K4: при удалении записи файл удаляется с диска."""
    if instance.image:
        instance.image.delete(save=False)


class ProfileReaction(models.Model):
    """
    K2: модель взаимодействия Лайк/Дизлайк.
    Одно поле is_like: True = лайк, False = дизлайк.
    Уникальный constraint: один пользователь может оценить другого только один раз.
    """

    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="given_reactions",
        verbose_name="Кто оценил",
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_reactions",
        verbose_name="Кого оценили",
    )
    is_like = models.BooleanField(verbose_name="Лайк (True) / Дизлайк (False)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["from_user", "to_user"],
                name="unique_user_reaction",
            )
        ]
        ordering = ["-created_at"]
        verbose_name = "Реакция (лайк/дизлайк)"
        verbose_name_plural = "Реакции"

    def __str__(self):
        kind = "лайк" if self.is_like else "дизлайк"
        return f"{self.from_user} → {self.to_user}: {kind}"

    def clean(self):
        super().clean()
        if self.from_user_id == self.to_user_id:
            raise ValidationError("Нельзя оценивать самого себя.")


class ViewHistory(models.Model):
    """K3: история просмотренных профилей."""

    viewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="view_history",
        verbose_name="Смотрел",
    )
    viewed = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="was_viewed_by",
        verbose_name="Смотрели",
    )
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-viewed_at"]
        verbose_name = "Просмотр профиля"
        verbose_name_plural = "Просмотры"


class DateInvite(models.Model):
    """K3: приглашение на свидание / обмен контактами."""

    STATUS_CHOICES = [
        ("pending", "Ожидает"),
        ("accepted", "Принято"),
        ("declined", "Отклонено"),
    ]

    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_invites",
        verbose_name="Отправитель",
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_invites",
        verbose_name="Получатель",
    )
    invite_type = models.CharField(
        max_length=20,
        choices=[("date", "Свидание"), ("contact", "Обмен контактами")],
        default="date",
        verbose_name="Тип приглашения",
    )
    message = models.TextField(blank=True, verbose_name="Сообщение")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["from_user", "to_user", "invite_type"],
                name="unique_invite",
            )
        ]
        ordering = ["-created_at"]
        verbose_name = "Приглашение"
        verbose_name_plural = "Приглашения"
