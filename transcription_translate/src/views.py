import json
import os
import uuid

from django.conf import settings
from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import VideoProcess
from .producer import send_to_kafka
from .utils.decorators import rate_limit

# DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "media/download")
DOWNLOAD_DIR = os.path.join(os.getcwd(), "download")


class TranscriptionView(APIView):
    @method_decorator(rate_limit(max_requests=5, time_window=600))
    def post(self, request):
        video_url = request.data.get("videoUrl")
        to_language = request.data.get("translate_language", "en")
        from_language = request.data.get("language", "en")
        print(16, video_url, to_language, from_language)
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        user_ip = get_client_ip(request)
        # Create the message payload
        message = {
            "video_url": video_url,
            "to_language": to_language,
            "task_id": task_id,
            "from_language": from_language,
            "user_ip": user_ip,
        }

        # Produce the message to Kafka
        send_to_kafka(message)

        return Response({"task_id": task_id}, status=status.HTTP_202_ACCEPTED)


class UploadVideoFileView(APIView):
    @method_decorator(rate_limit(max_requests=5, time_window=600))
    def post(self, request):
        video_file = request.FILES.get("file")
        to_language = request.data.get("translate_language", "en")
        from_language = request.data.get("language", "en")

        if not video_file:
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Generate a unique task ID
        task_id = str(uuid.uuid4())

        # Save the uploaded file to a temporary directory
        file_path = os.path.join(DOWNLOAD_DIR, video_file.name)
        with open(file_path, "wb+") as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)
        user_ip = get_client_ip(request)
        # Create the message payload
        message = {
            "file_path": file_path,
            "to_language": to_language,
            "task_id": task_id,
            "from_language": from_language,
            "user_ip": user_ip,
        }

        # Produce the message to Kafka
        send_to_kafka(message, "file-upload")

        return Response({"task_id": task_id}, status=status.HTTP_202_ACCEPTED)


def get_client_ip(request):
    """Utility function to get the client IP address from the request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


class TaskStatusView(APIView):
    def get(self, request, task_id):
        try:
            # Retrieve the VideoProcess record from the database using the task_id
            video_process = VideoProcess.objects.get(task_id=task_id)

            # Check the status of the video process
            if video_process.status == "pending":
                return Response({"status": "pending"}, status=status.HTTP_200_OK)
            elif video_process.status == "processing":
                return Response(
                    {
                        "status": "processing",
                    },
                    status=status.HTTP_200_OK,
                )
            elif video_process.status == "completed":
                return Response(
                    {"status": "completed", "url": video_process.output_file_url},
                    status=status.HTTP_200_OK,
                )
            elif video_process.status == "failed":
                return Response(
                    {"status": "failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            else:
                return Response(
                    {"status": video_process.status}, status=status.HTTP_200_OK
                )

        except VideoProcess.DoesNotExist:
            return Response(
                {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
            )


class SRTDownloadView(APIView):
    def get(self, request, task_id):
        srt_file_path = f"{task_id}.srt"
        if os.path.exists(srt_file_path):
            return FileResponse(
                open(srt_file_path, "rb"), as_attachment=True, filename=f"{task_id}.srt"
            )
        return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)


@csrf_exempt
def create_video_process(request):
    if request.method == "POST":
        data = json.loads(request.body)
        video_url = data.get("video_url")
        task_id = data.get("task_id")

        if not video_url or not task_id:
            return JsonResponse(
                {"error": "video_url and task_id are required fields."}, status=400
            )

        video_process = VideoProcess.objects.create(
            video_url=video_url, task_id=task_id
        )
        return JsonResponse({"id": video_process.id}, status=201)


@csrf_exempt
def get_video_process(request, id):
    try:
        video_process = VideoProcess.objects.get(id=id)
        response_data = {
            "id": video_process.id,
            "video_url": video_process.video_url,
            "task_id": video_process.task_id,
            "status": video_process.status,
            "created_at": video_process.created_at,
            "updated_at": video_process.updated_at,
        }
        return JsonResponse(response_data)
    except VideoProcess.DoesNotExist:
        return HttpResponseNotFound("VideoProcess not found")


@csrf_exempt
def get_videos_by_user_ip(request):
    if request.method == "GET":
        user_ip = request.GET.get("user_ip")

        if not user_ip:
            return JsonResponse({"error": "user_ip parameter is required."}, status=400)

        # Retrieve all VideoProcess entries for the given user_ip
        video_processes = VideoProcess.objects.filter(user_ip=user_ip)

        # Extract video_url from each VideoProcess entry
        video_urls = [video.video_url for video in video_processes]

        return JsonResponse({"video_urls": video_urls}, status=200)

    return JsonResponse({"error": "GET request required."}, status=405)


@csrf_exempt
def update_video_process(request, id):
    try:
        video_process = VideoProcess.objects.get(id=id)
        data = json.loads(request.body)

        video_process.video_url = data.get("video_url", video_process.video_url)
        video_process.task_id = data.get("task_id", video_process.task_id)
        video_process.status = data.get("status", video_process.status)

        video_process.save()
        response_data = {
            "id": video_process.id,
            "video_url": video_process.video_url,
            "task_id": video_process.task_id,
            "status": video_process.status,
            "created_at": video_process.created_at,
            "updated_at": video_process.updated_at,
        }
        return JsonResponse(response_data)
    except VideoProcess.DoesNotExist:
        return HttpResponseNotFound("VideoProcess not found")


@csrf_exempt
def delete_video_process(request, id):
    try:
        video_process = VideoProcess.objects.get(id=id)
        video_process.delete()
        return JsonResponse(
            {"message": "Video process deleted successfully."}, status=200
        )
    except VideoProcess.DoesNotExist:
        return HttpResponseNotFound("VideoProcess not found")


def get_all_videos(request):
    videos = VideoProcess.objects.all()
    response_data = [
        {
            "id": video.id,
            "video_url": video.video_url,
            "task_id": video.task_id,
            "status": video.status,
            "created_at": video.created_at,
            "updated_at": video.updated_at,
        }
        for video in videos
    ]
    return JsonResponse(response_data, safe=False)
