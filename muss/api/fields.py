
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.translation import ugettext_lazy as _
from rest_framework.fields import FileField
from rest_framework.settings import api_settings


class CustomFileField(FileField):
    """
    Custom field field for clear field if this is empty
    """
    def to_internal_value(self, data):
        validate_data = True

        try:
            # `UploadedFile` objects should have name and size attributes.
            file_name = data.name
            file_size = data.size
        except AttributeError:
            data = InMemoryUploadedFile(
                file='',
                field_name='',
                name='',
                content_type='',
                size=0,
                charset=''
            )
            validate_data = False

        if validate_data:
            if not file_name:
                self.fail('no_name')
            if not self.allow_empty_file and not file_size:
                self.fail('empty')
            if self.max_length and len(file_name) > self.max_length:
                self.fail('max_length', max_length=self.max_length, length=len(file_name))

        return data
