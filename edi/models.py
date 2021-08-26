import os
from django.db import models
from django.conf import settings
# Create your models here.


class Document(models.Model):
    document = models.FileField(upload_to='')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return os.path.basename(self.document.name)

    def delete(self, using=None, keep_parents=False):
        try:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.document.name))
        except:
            pass
        super().delete()
