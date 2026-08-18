from django.db.models import Count, Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from users.models import User

from .filters import ProfileFilterSet
from .models import DateInvite, ProfilePhoto, ProfileReaction, ViewHistory
from .serializers import (DateInviteSerializer, ProfilePhotoSerializer,
                          ProfileReactionSerializer, UserDetailSerializer,
                          UserListSerializer, ViewHistorySerializer)


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    K5: оптимизация — prefetch photos + аннотация likes_count.
    Фильтрация по полу/возрасту/городу/статусу.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_class = ProfileFilterSet

    def get_queryset(self):
        return (
            User.objects.filter(is_active=True)
            .prefetch_related("photos")
            .annotate(
                likes_count=Count(
                    "received_reactions", filter=Q(received_reactions__is_like=True)
                )
            )
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer
        return UserListSerializer

    def retrieve(self, request, *args, **kwargs):
        """K3: при просмотре профиля сохраняем в историю."""
        instance = self.get_object()
        if request.user.is_authenticated and request.user.id != instance.id:
            ViewHistory.objects.create(viewer=request.user, viewed=instance)
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def random(self, request):
        """Просмотр случайного профиля с учётом фильтров."""
        queryset = self.filter_queryset(self.get_queryset())
        profile = queryset.order_by("?").first()
        if not profile:
            return Response({"detail": "Нет подходящих профилей"}, status=404)
        if request.user.is_authenticated and request.user.id != profile.id:
            ViewHistory.objects.create(viewer=request.user, viewed=profile)
        return Response(UserDetailSerializer(profile).data)


class ProfilePhotoViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """K4: управление фотографиями (создание, список, удаление)."""

    serializer_class = ProfilePhotoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProfilePhoto.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReactionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """K2: лайк/дизлайк."""

    serializer_class = ProfileReactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProfileReaction.objects.filter(from_user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)


class ViewHistoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """K3: история просмотренных профилей (только свои)."""

    serializer_class = ViewHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ViewHistory.objects.filter(viewer=self.request.user).select_related(
            "viewed"
        )


class DateInviteViewSet(viewsets.ModelViewSet):
    """K3: приглашения на свидание / обмен контактами."""

    serializer_class = DateInviteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return DateInvite.objects.filter(
            Q(from_user=user) | Q(to_user=user)
        ).select_related("from_user", "to_user")

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)
