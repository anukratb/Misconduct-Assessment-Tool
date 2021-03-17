from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.core.files.uploadhandler import MemoryFileUploadHandler, TemporaryFileUploadHandler


# ------------------------------------Custom File Handler------------------------------------
class MDPCustomInMemoryUploadedFile(InMemoryUploadedFile):
    """The custom InMemoryUploadedFile data type

    In our MDP project, we need to know the original file path to show the details when
    user asks. Therefore, we added the support of original file path to the file type.
    """

    def __init__(self, file, field_name, name, content_type, size, charset, content_type_extra=None):
        """Init our in memory file object

        Here we add "original_path" to the file type so that we can use the path.
        """
        super().__init__(file, field_name, name, content_type, size, charset, content_type_extra)
        self.original_path = name[:name.rfind('/')] + "/"


class MDPCustomMemoryFileUploadHandler(MemoryFileUploadHandler):
    """The custom file upload handler

    This file handler uses MDPCustomInMemoryUploadedFile we defined above to support
    saving the original file path on the server.
    Here we only need to rewrite the way to create file. Make it using our custom file type so that we can use path
    information later.
    """

    def file_complete(self, file_size):
        """Return a file object if this handler is activated."""
        if not self.activated:
            return

        self.file.seek(0)
        return MDPCustomInMemoryUploadedFile(
            file=self.file,
            field_name=self.field_name,
            name=self.file_name,
            content_type=self.content_type,
            size=file_size,
            charset=self.charset,
            content_type_extra=self.content_type_extra
        )


class MDPCustomTemporaryUploadedFile(TemporaryUploadedFile):
    """The custom TemporaryUploadedFile data type

    In our MDP project, we need to know the original file path to show the details when
    user asks. Therefore, we added the support of original file path to the file type.
    """
    def __init__(self, name, content_type, size, charset, content_type_extra=None):
        """Init our temporary file object

        Here we add "original_path" to the file type so that we can use the path.
        """
        super().__init__(name, content_type, size, charset, content_type_extra)
        self.original_path = name[:name.rfind('/')] + "/"


class MDPCustomTemporaryFileUploadHandler(TemporaryFileUploadHandler):
    """The custom file upload handler

    This file handler uses MDPCustomTemporaryUploadedFile we defined above to support
    saving the original file path on the server.
    Here we only need to rewrite the way to create file. Make it using our custom file type so that we can use path
    information later.
    """
    def new_file(self, *args, **kwargs):
        super().new_file(*args, **kwargs)
        self.file = MDPCustomTemporaryUploadedFile(self.file_name, self.content_type, 0, self.charset,
                                                   self.content_type_extra)
