from django.shortcuts import render
from django.views import generic
from django.http import JsonResponse

from .env_settings import *


class SaveView(generic.View):
    """Class handles saving currently active workspace for user
    """

    def post(self, request, *args, **kwargs):
        """Method handles POST requests to this endpoint. Expects `name` to be 
            path parameter, and returns JSON formatted response to indicate 
            success of the command. When handler is invoked, it saves the 
            current workspace.
        
        :param request: Request that has been made
        :type request: HttpRequest
        :return: JSON encoded response indicating command success
        :rtype: HttpResponse
        """

        # TODO: could check if user is working on a workspace to save progress 
        # on the workspace (otherwise need to delete and save again)
        success = save_workspace(request, kwargs['name'])

        return JsonResponse({'success': success})


class ListView(generic.View):
    """Class handles listing all user workspaces
    """

    def get(self, request, *args, **kwargs):
        """Method handles GET requests to this endpoint. Returns JSON formatted 
            response to indicate success of the command as well as list of all 
            user saved workspaces. This handler reads user workspaces.
        
        :param request: Request that has been made
        :type request: HttpRequest
        :return: JSON encoded response indicating command success
        :rtype: HttpResponse
        """
        workspaces = list_workspaces(request)

        return JsonResponse({
            'success': True,
            'workspaces': workspaces
        })


class LoadView(generic.View):
    """Class handles loading a new workspace for user
    """
    
    def post(self, request, *args, **kwargs):
        """Method handles POST requests to this endpoint. Expects `name` to be 
            path parameter, and returns JSON formatted response to indicate 
            success of the command. When handler is invoked, it loads the 
            required workspace for user.
        
        :param request: Request that has been made
        :type request: HttpRequest
        :return: JSON encoded response indicating command success
        :rtype: HttpResponse
        """
        success = load_workspace(request, kwargs['name'])

        return JsonResponse({'success': success})


class DeleteView(generic.View):
    """Class handles deleting saved workspace for user
    """

    def post(self, request, *args, **kwargs):
        """Method handles POST requests to this endpoint. Expects `name` to be 
            path parameter, and returns JSON formatted response to indicate 
            success of the command. When handler is invoked, it deletes the 
            workspace indicated. Command returns success even if such workspace 
            did not exist
        
        :param request: Request that has been made
        :type request: HttpRequest
        :return: JSON encoded response indicating command success
        :rtype: HttpResponse
        """
        delete_workspace(request, kwargs['name'])

        return JsonResponse({'success': True})
