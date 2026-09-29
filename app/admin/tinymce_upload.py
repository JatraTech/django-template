import mimetypes
import os
from uuid import uuid4

from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.http import require_POST

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml",
}


@staff_member_required
@require_POST
def tinymce_upload(request):
    uploaded = request.FILES.get("file")
    if not uploaded:
        return JsonResponse({"error": "No file provided."}, status=400)

    if uploaded.size > MAX_UPLOAD_BYTES:
        return JsonResponse({"error": "File exceeds 5 MB limit."}, status=400)

    content_type = uploaded.content_type or mimetypes.guess_type(uploaded.name)[0] or ""
    if content_type not in ALLOWED_IMAGE_TYPES:
        return JsonResponse({"error": "Only image uploads are allowed."}, status=400)

    _, ext = os.path.splitext(uploaded.name)
    ext = ext.lower() if ext else mimetypes.guess_extension(content_type) or ".bin"
    path = default_storage.save(f"editor/{uuid4().hex}{ext}", uploaded)
    url = default_storage.url(path)

    if not url.startswith(("http://", "https://")):
        url = request.build_absolute_uri(url)

    return JsonResponse({"location": url})
