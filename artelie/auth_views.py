from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        access = serializer.validated_data["access"]
        refresh = serializer.validated_data["refresh"]
        response = Response({"access": access}, status=status.HTTP_200_OK)
        cookie_name = getattr(settings, "REFRESH_TOKEN_COOKIE_NAME", "refresh_token")
        response.set_cookie(
            cookie_name,
            refresh,
            httponly=getattr(settings, "REFRESH_TOKEN_COOKIE_HTTPONLY", True),
            secure=getattr(settings, "REFRESH_TOKEN_COOKIE_SECURE", False),
            samesite=getattr(settings, "REFRESH_TOKEN_COOKIE_SAMESITE", "Lax"),
            path=getattr(settings, "REFRESH_TOKEN_COOKIE_PATH", "/api/token/refresh/")
        )
        return response


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        cookie_name = getattr(settings, "REFRESH_TOKEN_COOKIE_NAME", "refresh_token")
        raw_refresh = request.COOKIES.get(cookie_name)
        if not raw_refresh:
            return Response({"detail": "Refresh token cookie not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = TokenRefreshSerializer(data={"refresh": raw_refresh})
        serializer.is_valid(raise_exception=True)
        data = {"access": serializer.validated_data["access"]}
        if "refresh" in serializer.validated_data:
            new_refresh = serializer.validated_data["refresh"]
            response = Response(data, status=status.HTTP_200_OK)
            response.set_cookie(
                cookie_name,
                new_refresh,
                httponly=getattr(settings, "REFRESH_TOKEN_COOKIE_HTTPONLY", True),
                secure=getattr(settings, "REFRESH_TOKEN_COOKIE_SECURE", False),
                samesite=getattr(settings, "REFRESH_TOKEN_COOKIE_SAMESITE", "Lax"),
                path=getattr(settings, "REFRESH_TOKEN_COOKIE_PATH", "/api/token/refresh/")
            )
            return response
        return Response(data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        cookie_name = getattr(settings, "REFRESH_TOKEN_COOKIE_NAME", "refresh_token")
        raw_refresh = request.COOKIES.get(cookie_name)
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(cookie_name, path=getattr(settings, "REFRESH_TOKEN_COOKIE_PATH", "/api/token/refresh/"))
        if raw_refresh:
            try:
                token = RefreshToken(raw_refresh)
                token.blacklist()
            except Exception:
                pass
        return response
