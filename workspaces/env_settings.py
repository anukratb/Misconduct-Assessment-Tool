# import os
# import shutil

# from misconduct_detection_app.env_settings import APP_PATH, get_user_paths


# def get_workspaces_dir(request):
#     """Function computes user workspaces folder name based on logged in user 
#         instance. If workspaces path does not yet exist for user, it is created.
    
#     :param request: Request that has been made and contains user credentials
#     :type request: HttpRequest
#     :return: Subdirectory name for user saved workspaces
#     :rtype: str
#     """
#     ws_path = os.path.join(APP_PATH, "workspaces", "user_{}".format(request.user.id))

#     if not os.path.exists(ws_path):
#         os.makedirs(ws_path)

#     return ws_path


# def save_workspace(request, name):
#     """Function saves current workspace under a given name
    
#     :param request: Request that has been made, with user credentials indicating 
#         active session
#     :type request: HttpRequest
#     :param name: The desired name for the workspace
#     :type name: str
#     :return: Success indicator, stating if action was successful. Returns False, 
#         if workspace with such name already exists
#     :rtype: bool
#     """
#     if name in list_workspaces(request):
#         return False

#     workspaces_path = get_workspaces_dir(request)
#     ws_path = os.path.join(workspaces_path, name)
#     os.mkdir(ws_path)

#     paths = get_user_paths(request.user)

#     for src, target in zip(paths, ["uploads", "reports"]):
#         shutil.copytree(src, os.path.join(ws_path, target))

#     return True


# def list_workspaces(request):
#     """Function lists all saved workspaces for logged in user
    
#     :param request: Request that has been made and contains user credentials
#     :type request: HttpRequest
#     :return: Names of all user workspaces
#     :rtype: list of str
#     """
#     ws_path = get_workspaces_dir(request)

#     return os.listdir(ws_path)


# def load_workspace(request, name):
#     """Function loads a saved workspace as the active workspace. The current 
#         active workspace will be overwritten without being saved before.
    
#     :param request: Request that has been made and contains user credentials
#     :type request: HttpRequest
#     :param name: The name of the workspace to be loaded
#     :type name: str
#     :return: Success indicator, that indicates if action was successful. Returns 
#         False, if workspace with given name does not exist
#     :rtype: bool
#     """
#     if name not in list_workspaces(request):
#         return False
    
#     workspaces_path = get_workspaces_dir(request)
#     ws_path = os.path.join(workspaces_path, name)

#     paths = get_user_paths(request.user)

#     for src, target in zip(["uploads", "reports"], paths):
#         shutil.copytree(os.path.join(ws_path, src), target)

#     return True


# def delete_workspace(request, name):
#     """Function deletes a saved workspace, if such workspace exists
    
#     :param request: Request that has been made and contains user credentials
#     :type request: HttpRequest
#     :param name: The name of the workspace to delete
#     :type name: str
#     """
#     workspaces_path = get_workspaces_dir(request)
#     ws_path = os.path.join(ws_path, name)
    
#     if os.path.exists(ws_path):
#         shutil.rmtree(ws_path)
