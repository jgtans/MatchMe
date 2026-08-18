from django.db.models import Count, Q
from rest_framework import serializers

from users.models import User

from .models import DateInvite, ProfilePhoto, ProfileReaction, ViewHistory


class UserListSerializer(serializers.ModelSerializer):
    """Краткий профиль для ленты."""

    main_photo = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "gender",
            "age",
            "city",
            "status",
            "main_photo",
            "likes_count",
        ]

    def get_main_photo(self, obj):
        main = obj.photos.filter(is_main=True).first()
        return main.image.url if main and main.image else None


class ProfilePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilePhoto
        fields = ["id", "image", "is_main", "uploaded_at"]
        read_only_fields = ["uploaded_at"]


class UserDetailSerializer(serializers.ModelSerializer):
    """Полный профиль для детальной страницы (K5 — prefetch photos)."""

    photos = ProfilePhotoSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "gender",
            "age",
            "city",
            "hobbies",
            "status",
            "bio",
            "photos",
            "likes_count",
        ]

    def get_likes_count(self, obj):
        return ProfileReaction.objects.filter(to_user=obj, is_like=True).count()


class ProfileReactionSerializer(serializers.ModelSerializer):
    """K2: лайк/дизлайк (K6: валидация 'нельзя себя лайкать')."""

    class Meta:
        model = ProfileReaction
        fields = ["id", "to_user", "is_like", "created_at"]
        read_only_fields = ["created_at"]

    def validate(self, attrs):
        if attrs["to_user_id"] == self.context["request"].user.id:
            raise serializers.ValidationError("Нельзя оценивать самого себя.")
        return attrs


class ViewHistorySerializer(serializers.ModelSerializer):
    viewed = UserListSerializer(read_only=True)

    class Meta:
        model = ViewHistory
        fields = ["id", "viewed", "viewed_at"]


class DateInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DateInvite
        fields = ["id", "to_user", "invite_type", "message", "status", "created_at"]
        read_only_fields = ["status", "created_at"]
