from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from profiles.views import (DateInviteViewSet, ProfilePhotoViewSet,
                            ProfileViewSet, ReactionViewSet,
                            ViewHistoryViewSet)

router = DefaultRouter()
router.register("profiles", ProfileViewSet, basename="profiles")
router.register("photos", ProfilePhotoViewSet, basename="photos")
router.register("reactions", ReactionViewSet, basename="reactions")
router.register("history", ViewHistoryViewSet, basename="history")
router.register("invites", DateInviteViewSet, basename="invites")

urlpatterns = [
    path("", RedirectView.as_view(url="/swagger/", permanent=False)),
    path("admin/", admin.site.urls),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    path("api/", include(router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
