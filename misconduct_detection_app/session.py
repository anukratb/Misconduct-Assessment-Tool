import os
import shutil

from django.contrib.sessions.backends.db import SessionStore as DBSessionStore
from django.utils import timezone

from .env_settings import get_session_paths


class SessionStore(DBSessionStore):
    """Class implements session storage for managing user session data. This 
        class inherits from DB session store as it is the default for Django 
        (could be any other store). Class implements additional behaviour on 
        session cleanup to remove any files stored for anonymous users.
    """

    @classmethod
    def clear_expired(cls):
        """Method clears all sessions that are expired at this point. Sessions 
            are deleted from session store (DB), as well as user uploaded and 
            result files are removed from file system.
        """
        expired_sessions = cls.get_model_class().objects.filter(expire_date__lt=timezone.now())

        for sess in expired_sessions:
            print("Removing session: {}".format(sess.session_key))
            paths_to_clear = get_session_paths(sess)
            for path in paths_to_clear:
                if os.path.exists(path):
                    shutil.rmtree(path)

            sess.delete()
