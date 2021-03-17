"""misconduct_detection_project Context Processors Configuration

Put the data need to be shared across pages here. For example, you can see
https://stackoverflow.com/questions/3221592/how-to-pass-common-dictionary-data-to-every-page-in-django

or you can check Django document
https://docs.djangoproject.com/en/dev/ref/templates/api/
for more information.
"""
from .env_settings import get_segments_path
from .env_settings import get_folder_path
from .env_settings import get_file_to_compare_path
from .env_settings import get_results_path
from .env_settings import get_configs_path
from .env_settings import null_detection_libs
import os
import json
from django.core.serializers.json import DjangoJSONEncoder

import logging

logger = logging.getLogger(__name__)


def segments_exist(segments_path):
    """Function determines if there are segments in the given path. This 
        function does not check if any segment is selected.
    
    :param segments_path: The path to segments directory
    :type segments_path: str
    :return: Indicator if there exist at least one valid segment
    :rtype: bool
    """
    if not os.path.exists(segments_path):
        # Segments directory does not exist for user
        return False

    files = os.listdir(segments_path)
    
    if not files:
        # Segments directory empty for user
        return False

    if len(files) == 1 and os.path.exists(os.path.join(segments_path, "include_segments_path")):
        # There are no segment files, only copy from last detection
        return False

    # There is at least one valid segment file
    return True


def generate_uploaded_file_list(request):
    """Read and fetch user files on the server and return to front end.

    If the required files are not exist, the return values will be ["NOFOLDEREXISTS"] (a list contains a string).
    Otherwise, return value accordingly.
    :param request: request
    :type request: HttpRequest
    :return: file_to_compare_path_list(uploaded single file), results_path_list(results), folder_path_list(uploaded
    folder), segments_path_list(selected segments from last time), configs_path_list (configs saved by the user)
    :rtype: (list, list, list, list, str/dict)
    """
    logger.debug("Generating uploaded file list for request %s", request)
    file_to_compare_path = get_file_to_compare_path(request)
    results_path = get_results_path(request)
    folder_path = get_folder_path(request)
    segments_path = get_segments_path(request)
    configs_path = os.path.join(get_configs_path(request), "configs.txt")
    if os.path.exists(file_to_compare_path):
        file_to_compare_path_list = os.listdir(file_to_compare_path)
    else:
        file_to_compare_path_list = ["NOFOLDEREXISTS"]
    if segments_exist(segments_path) :
        segments_path_list = ["SEGMENTSEXISTS"]
    else:
        segments_path_list = ["NOFOLDEREXISTS"]
    if os.path.exists(results_path):
        results_path_list = ["RESULTSEXISTS"]
    else:
        results_path_list = ["NOFOLDEREXISTS"]

    if os.path.exists(configs_path):
        configs_path_list = {}
        with open(os.path.join(get_configs_path(request), "configs.txt")) as f:
            file_lines = f.readlines()
        for line in file_lines:
            line = line.strip('\n')
            paraname, paradata = line.split(",")
            configs_path_list[paraname] = paradata
    else:
        configs_path_list = "NOFOLDEREXISTS"

    folder_path_list = []
    for (dir_path, dir_names, file_names) in os.walk(folder_path):
        for file_name in file_names:
            folder_path_list.append(os.path.join(dir_path, file_name))
    if len(folder_path_list) == 0:
        folder_path_list = ["NOFOLDEREXISTS"]
    return file_to_compare_path_list, results_path_list, folder_path_list, segments_path_list, configs_path_list


def return_uploaded_files(request):
    """Return the uploaded file information to front end

    :param request: request
    :type request: HttpRequest
    :return: uploaded file information, file_to_compare_path_list, results_path_list, folder_path_list and
    segments_path_list
    :rtype: (list, list, list, list, dict)
    """
    logger.debug("Returning uploaded files list for request %s", request)
    file_to_compare_path_list, results_path_list, folder_path_list, segments_path_list, configs_path_list \
        = generate_uploaded_file_list(request)
    context = {
        "fileToComparePathList": json.dumps(file_to_compare_path_list, cls=DjangoJSONEncoder),
        "resultsPathList": json.dumps(results_path_list, cls=DjangoJSONEncoder),
        "folderPathList": json.dumps(folder_path_list, cls=DjangoJSONEncoder),
        "segmentsPathList": json.dumps(segments_path_list, cls=DjangoJSONEncoder),
        "configsList": json.dumps(configs_path_list, cls=DjangoJSONEncoder),
    }
    return context


def update_bottom_bar(request):
    """ Used to update the context of the bottom bar at the upload page
    Note: similar to return_uploaded_files, but returns a dict instead of a
    DjangoJSON Encoded dict that is used with templates

    :param request:
    :return:
    """
    logger.debug("Returning uploaded files list for request %s", request)
    file_to_compare_path_list, results_path_list, folder_path_list, segments_path_list, configs_path_list \
        = generate_uploaded_file_list(request)
    context = {
        "fileToComparePathList": file_to_compare_path_list,
        "resultsPathList": results_path_list,
        "folderPathList": folder_path_list,
        "segmentsPathList": segments_path_list,
        "configsList": configs_path_list,
    }
    return context

def return_supported_detection_lib(request):
    logger.debug("Return supported detection libraries")
    all_detection_lib_support_languages = {}
    for detection_lib_name in null_detection_libs.keys():
        all_detection_lib_support_languages[detection_lib_name] = \
            null_detection_libs[detection_lib_name].file_language_supported
    context = {
        "detectionLibList": json.dumps(all_detection_lib_support_languages, cls=DjangoJSONEncoder),
    }
    return context
