from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, parsers
from musics.models import *

from .serializers import SongCreateSerializer


class SongCreateAPIView(APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, *args, **kwargs):
        serializer = SongCreateSerializer(data=request.data)
        if serializer.is_valid():
            song = serializer.save()
            return Response(
                {
                    "message": "آهنگ با موفقیت ایجاد شد.",
                    "id": song.id,
                    "title": song.title,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SongCreateOptionsAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        data = {
            "tags": Tag.objects.values("id", "title"),
            "albums": Album.objects.values("id", "title"),
            "categories": Category.objects.values("id", "title"),
            "singers": Singer.objects.values("id", "name"),
            "languages": Language.objects.values("id", "name"),
        }
        return Response(data)









