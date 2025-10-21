from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from artelie.models.review import Review
from artelie.serializers.review import ReviewSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)