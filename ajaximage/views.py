import os
import json
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.utils.functional import allow_lazy
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import unicodedata
import re
import six
from .image import resize
from .forms import FileForm

class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

try:
    from django.utils.text import slugify
except:
    def slugify(value):
        """
        Converts to lowercase, removes non-word characters (alphanumerics and
        underscores) and converts spaces to hyphens. Also strips leading and
        trailing whitespace.
        """
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub('[^\w\s-]', '', value).strip().lower()
        return mark_safe(re.sub('[-\s]+', '-', value))
    slugify = allow_lazy(slugify, six.text_type)


UPLOAD_PATH = getattr(settings, 'AJAXIMAGE_DIR', 'ajaximage/')
AUTH_TEST = getattr(settings, 'AJAXIMAGE_AUTH_TEST', lambda u: u.is_staff)
FILENAME_NORMALIZER = getattr(settings, 'AJAXIMAGE_FILENAME_NORMALIZER', slugify)


@require_POST
@user_passes_test(AUTH_TEST)
def ajaximage(request, upload_to=None, max_width=None, max_height=None, crop=None, form_class=FileForm):
    form = form_class(request.POST, request.FILES)
    if form.is_valid():
        file_ = form.cleaned_data['file']

        image_types = ['image/png', 'image/jpg', 'image/jpeg', 'image/pjpeg',
                       'image/gif']

        if file_.content_type not in image_types:
            data = json.dumps({'error': 'Bad image format.'})
            return HttpResponse(data, content_type="application/json", status=403)

        file_ = resize(file_, max_width, max_height, crop)
        file_name, extension = os.path.splitext(file_.name)
        safe_name = '{0}{1}'.format(FILENAME_NORMALIZER(file_name), extension)

        name = os.path.join(upload_to or UPLOAD_PATH, safe_name)
        storage = OverwriteStorage()
        path = storage.save(name, file_)
        url = storage.url(path)

        return HttpResponse(json.dumps({'url': url, 'filename': path}))

    return HttpResponse(status=403)


@require_POST
@user_passes_test(AUTH_TEST)
def ajaxfile(request, upload_to=None, form_class=FileForm):
    form = form_class(request.POST, request.FILES)
    if form.is_valid():
        file_ = form.cleaned_data['file']

        file_name, extension = os.path.splitext(file_.name)
        safe_name = '{0}{1}'.format(FILENAME_NORMALIZER(file_name), extension)

        name = os.path.join(upload_to or UPLOAD_PATH, safe_name)
        storage = OverwriteStorage()
        path = storage.save(name, file_)
        url = storage.url(path)

        return HttpResponse(json.dumps({'url': url, 'filename': path}))

    return HttpResponse(status=403)
