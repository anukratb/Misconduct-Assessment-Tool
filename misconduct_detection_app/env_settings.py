import shutil

from django.conf import settings

from .detection_libs import Jplag, SID
import os
from filecmp import cmp

# Global system parameters defined here.
APP_PATH = "misconduct_detection_app"
DETECTION_LIBS = {}
SUPPORTED_PROGRAMMING_LANGUAGE_EXTENSION = [
    "java", "py", "c", "cpp", "cs", "txt", "m"
]  # the supported language of this tool

# The following default path is used when user is unknown. Which is 'default' situation
DEFAULT_FILE_TO_COMPARE_WITH_PATH = os.path.join(APP_PATH, "uploads", "Default", "singlefiles")
DEFAULT_FOLDER_PATH = os.path.join(APP_PATH, "uploads", "Default", "folders")
DEFAULT_TEMP_WORKING_PATH = os.path.join(APP_PATH, "uploads", "Default", "temp")
DEFAULT_RESULTS_PATH = os.path.join(APP_PATH, "results", "Default")
DEFAULT_SEGMENTS_PATH = os.path.join(APP_PATH, "uploads", "Default", "segments")
DEFAULT_CONFIGS_PATH = os.path.join(APP_PATH, "uploads", "Default", "configs")


def get_folder_from_session(sess):
    """Function computes user folder name based on the Django session instance 
        provided.
    
    :param sess: User session
    :type sess: Session
    :return: Subdirectory name for user specific files
    :rtype: str
    """
    return "guest_{}".format(sess.session_key)


def get_folder_from_user(user):
    """Function computes user folder name based on logged in user instance.
    
    :param user: Logged in user
    :type user: User
    :return: Subdirectory name for user specific files
    :rtype: str
    """
    return "authenticated_{}".format(user.id)


def get_user_id(request):
    """Function retrieves user subdirectory name where all uploaded and result 
        files will be stored
    
    :param request: Request that has been made and contains user credentials
    :type request: HttpRequest
    :return: Subdirectory name for user specific files
    :rtype: str
    """
    if request.user.is_authenticated:
        request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        return get_folder_from_user(request.user)

    request.session.set_expiry(86400)

    return get_folder_from_session(request.session)


def get_session_paths(sess):
    """Function retrieves all paths used to store data for user session. This 
        function is intended for use with anonymous user sessions, thus takes 
        Session as a parameter, instead of HttpRequest as majority of other 
        functions
    
    :param sess: Anonymous user session
    :type sess: Session
    :return: List of directories used to store data for user session - uploaded 
        files and result files
    :rtype: list of str
    """
    uploads_dir = os.path.join(APP_PATH, "uploads", get_folder_from_session(sess))
    results_dir = os.path.join(APP_PATH, "results", get_folder_from_session(sess))

    return [uploads_dir, results_dir]


def get_user_paths(user):
    """Function retrieves all paths used to store data for user account. This 
        function is intended for use with logged in user sessions, thus takes 
        User as a parameter, instead of HttpRequest as majority of other 
        functions
    
    :param user: Logged in user instance
    :type user: User
    :return: List of directories used to store data for logged in user session -
        uploaded files and result files
    :rtype: list of str
    """
    uploads_dir = os.path.join(APP_PATH, "uploads", get_folder_from_user(user))

    #results_dir = os.path.join(APP_PATH, "results", get_folder_from_user(user))
    results_dir = os.path.join(APP_PATH, "results")

    return [uploads_dir, results_dir]


# Dynamic file path getter.
def get_file_to_compare_path(request):
    """Dynamically get the "file" path

    :param request: request
    :type request: HttpRequest
    :return: path of the single uploaded file
    :rtype: str
    """
    file_to_compare_path = os.path.join(APP_PATH, "uploads", get_user_id(request), "singlefiles")
    return file_to_compare_path


def get_folder_path(request):
    """Dynamically get the "folder" path

    :param request: request
    :type request: HttpRequest
    :return: path of the uploaded folder
    :rtype: str
    """
    folder_path = os.path.join(APP_PATH, "uploads", get_user_id(request), "folders")
    return folder_path


def get_list_of_files(dirName):
    # source: https://thispointer.com/python-how-to-get-list-of-files-in-directory-and-sub-directories/
    # create a list of file and sub directories
    # names in the given directory
    if not os.path.exists(dirName):
        return []

    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + get_list_of_files(fullPath)
        else:
            allFiles.append(fullPath)

    return allFiles


def uploaded_file_dir_in_folder(request):
    """
    Check if the uploaded file is included in the uploaded folder and return the 
        path for the submission folder

    :param request:
    :return: The submission directory for the uploaded file or None if file is 
        not included
    """
    file_path = get_file_to_compare_path(request)
    single_file_dir = get_list_of_files(file_path)
    if len(single_file_dir) == 0:
        return None
    file = single_file_dir[0]
    folder_path = get_folder_path(request)
    folder_files = get_list_of_files(folder_path)
    print(folder_path)
    print('EMRANNN')

    for folder_file in folder_files:
        if cmp(file, folder_file):
            reduced_path = folder_file
            path_end = []
            while reduced_path != folder_path:
                reduced_path, last = os.path.split(reduced_path)
                path_end.append(last)
            return os.path.join(folder_path, path_end[-1])

    return None


def number_of_submissions(request):
    """
    Helper function to find the number of submissions of an uploaded folder
    :param request:
    :return:
    """
    number_of_submissions = 0
    if os.path.exists(get_folder_path(request)):
        d = os.path.join(get_folder_path(request), os.listdir(get_folder_path(request))[0])
        number_of_submissions = len([os.path.join(d, o) for o in os.listdir(d)
                                     if os.path.isdir(os.path.join(d, o))])
        # number_of_submissions = len(os.listdir(
        #    os.path.join(get_folder_path(request), os.listdir(get_folder_path(request))[0])))
    return number_of_submissions

def get_temp_working_path(request):
    """Dynamically get the temp working folder path

    :param request: request
    :type request: HttpRequest
    :return: path of the temp working folder
    :rtype: str
    """
    temp_working_path = os.path.join(APP_PATH, "uploads", get_user_id(request), "temp")
    return temp_working_path


def get_results_path(request):
    """Dynamically get the results folder path

    :param request: request
    :type request: HttpRequest
    :return: path of the results
    :rtype: str
    """
    results_path = os.path.join(APP_PATH, "results", get_user_id(request))
    return results_path


def get_segments_path(request):
    """Dynamically get the segment folder path

    :param request: request
    :type request: HttpRequest
    :return: path to save user selected segments
    :rtype: str
    """
    segments_path = os.path.join(APP_PATH, "uploads", get_user_id(request), "segments")
    return segments_path


def get_configs_path(request):
    """Dynamically get the config folder path

    :param request: request
    :type request: HttpRequest
    :return: path to save user selected segments
    :rtype: str
    """
    configs_path = os.path.join(APP_PATH, "uploads", get_user_id(request), "configs")
    return configs_path


# Define each detection package creator as a function so that we can dynamically produce paths
def jplag_default_creator(request, extra_settings):
    # First generate the segments which are included
    with open(get_configs_path(request) + "/" + "checked_boxes" + '.txt', 'r') as f:
        checked_segments = f.read()
    include_segments_path = os.path.join(get_segments_path(request), "include_segments_path")
    if os.path.exists(include_segments_path):
        shutil.rmtree(include_segments_path)
    if not os.path.exists(include_segments_path):
        os.makedirs(include_segments_path)
    checked_segments = checked_segments.split(",")

    uploaded_file_name = get_file_to_compare_path(request)
    extension_name = os.listdir(uploaded_file_name)[0]
    extension_name = extension_name[extension_name.find("."):]

    for checked_segment in checked_segments:
        shutil.copy(os.path.join(get_segments_path(request), "Segment_" + checked_segment),
                    os.path.join(include_segments_path, "Segment_" + checked_segment + extension_name))

    # Decompress the extra parameters
    detection_language = extra_settings["detectionLanguage"]
    threshold = extra_settings["detectionThreshold"]

    # Return the JPlag object dynamically
    return Jplag(lib_path=os.path.join(APP_PATH, "detection_libs", "jplag-2.11.9-SNAPSHOT-jar-with-dependencies.jar"),
                 results_path=get_results_path(request), segments_path=include_segments_path,
                 folder_to_compare_path=get_folder_path(request), file_language=detection_language,
                 threshold=threshold)


def sid_default_creator(request, extra_settings):
    # First generate the segments which are included
    with open(get_configs_path(request) + "/" + "checked_boxes" + '.txt', 'r') as f:
        checked_segments = f.read()
    include_segments_path = os.path.join(get_segments_path(request), "include_segments_path")
    if os.path.exists(include_segments_path):
        shutil.rmtree(include_segments_path)
    if not os.path.exists(include_segments_path):
        os.makedirs(include_segments_path)
    checked_segments = checked_segments.split(",")

    uploaded_file_name = get_file_to_compare_path(request)
    extension_name = os.listdir(uploaded_file_name)[0]
    extension_name = extension_name[extension_name.find("."):]

    for checked_segment in checked_segments:
        shutil.copy(os.path.join(get_segments_path(request), "Segment_" + checked_segment),
                    os.path.join(include_segments_path, "Segment_" + checked_segment + extension_name))

    # Decompress the extra parameters
    detection_language = extra_settings["detectionLanguage"]
    threshold = int(extra_settings["detectionThreshold"])

    # Return the JPlag object dynamically
    return SID(results_path=get_results_path(request), segments_path=include_segments_path,
               folder_to_compare_path=get_folder_path(request), file_language=detection_language,
               threshold=threshold)


# Register detection packages
detection_libs_configs = {
    "JPlag": jplag_default_creator,
    "SID": sid_default_creator,
}

# This dict contains the null detection lib objects, which is used to provide
# some basic information of the corresponding detection library(package). Such
# as supported programming language type here.
null_detection_libs = {
    "JPlag": Jplag(lib_path=os.path.join(APP_PATH, "detection_libs", "jplag-2.11.9-SNAPSHOT-jar-with-dependencies.jar"),
                   results_path="", segments_path="", folder_to_compare_path="", file_language="c/c++",
                   threshold="80%"),
    "SID": SID(results_path="", segments_path="", folder_to_compare_path="", file_language="python3"),
}


def auto_detect_programming_language(request):
    # Selection dict which will be used to provide selection
    selection_dict = {}
    for language in SUPPORTED_PROGRAMMING_LANGUAGE_EXTENSION:
        selection_dict[language] = language

    # Allocate default detection packages for different programming languages.
    # Here since we have only JPlag in this iteration, I allocated all programming languages to JPlag
    selection_dict["java"] = [["JPlag"], "java17"]
    selection_dict["py"] = [["JPlag", "SID"], "python3"]
    selection_dict["c"] = [["JPlag"], "c/c++"]
    selection_dict["cpp"] = [["JPlag"], "c/c++"]
    selection_dict["cs"] = [["JPlag"], "c#-1.2"]
    selection_dict["txt"] = [["JPlag"], "text"]
    selection_dict["m"] = [["SID"], "matlab"]

    # Raise not implemented errors
    for key in selection_dict.keys():
        if selection_dict[key] == key:
            raise NotImplementedError("Default detection package not allocated for " + key)

    # Return results based on previous settings and local file
    uploaded_file_name = get_file_to_compare_path(request)
    extension_name = os.listdir(uploaded_file_name)[0]
    extension_name = extension_name[extension_name.rfind(".") + 1:]
    try:
        return selection_dict[extension_name]
    except KeyError:
        print("Uploaded file not supported")
        return "FILE_TYPE_NOT_SUPPORTED"


def num_external_files(request):
    """Function calculates the number of files that are in the uploaded folder. 
        If the uploaded file is included in the submissions, then all files from 
        that specific submission are excluded from the count.
    
    :param request: Request that has been made and contains user credentials
    :type request: HttpRequest
    :return: The number of files uploaded (excluding the submission)
    :rtype: int
    """
    # calculate the number of files from other submissions
    folder_path = get_folder_path(request)
    folder_files = get_list_of_files(folder_path)

    submission_folder = uploaded_file_dir_in_folder(request)
    print(submission_folder)
    submission_files = []
    if submission_folder is not None:
        submission_files = get_list_of_files(submission_folder)

    return len(folder_files) - len(submission_files)

def get_workspaces_dir(request):
    """Function computes user workspaces folder name based on logged in user 
        instance. If workspaces path does not yet exist for user, it is created.
    
    :param request: Request that has been made and contains user credentials
    :type request: HttpRequest
    :return: Subdirectory name for user saved workspaces
    :rtype: str
    """
    ws_path = os.path.join(APP_PATH, "workspaces", "user_{}".format(request.user.id))

    if not os.path.exists(ws_path):
        os.makedirs(ws_path)

    return ws_path

