import shutil
import os
import pickle
import json

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import logout

from .env_settings import *
from . import context_processors

import logging
logger = logging.getLogger(__name__)

APP_PATH = "misconduct_detection_app"

# Create your views here.
# ------------------------------------Index------------------------------------
def index(request):
	"""The index page. Shows an initial choice between login and continuing as a
		guest if user has not made the choice yet. Otherwise shows Landing page 
		with instructions.

	:param request: request
	:type request: HttpRequest
	:return: render
	:rtype: render
	"""
	if request.user.is_authenticated or 'guest' in request.session:
		return render(request, 'misconduct_detection_app/welcome.html')

	return render(request, 'misconduct_detection_app/landing.html')

def guest_index(request):
	"""Proxy page for users willing to continue without logging in. This view 
		sets guest parameter in session and redirects to Landing page with 
		instructions.

	:param request: request
	:type request: HttpRequest
	:return: render
	:rtype: render
	"""
	request.session['guest'] = True
	return redirect('index')

def upload_index(request):
	"""The upload page

	:param request: request
	:type request: HttpRequest
	:return: render
	:rtype: render
	"""
	# if not request.user.is_authenticated or 'guest' not in request.session:
	#     return redirect('index')

	context = {
		"numberOfSubmissions": number_of_submissions(request),
	}
	return render(request, 'misconduct_detection_app/upload.html', context)


def uploaded_folder_index(request):
	""" The uploaded folder page

		:param request: request
		:type request: HttpRequest
		:return: render
		:rtype: render
	"""
	# if not request.user.is_authenticated or 'guest' not in request.session:
	#     return redirect('index')

	# Check if uploaded file is in uploaded folder
	is_file_included = "No"
	if uploaded_file_dir_in_folder(request) is not None:
		is_file_included = "Yes"
	context = {
		"numberOfSubmissions": number_of_submissions(request),
		"isFileIncluded": is_file_included
	}
	return render(request, 'misconduct_detection_app/uploadedFolder.html', context)

def select_index(request):
	"""The select page

	:param request: request
	:type request: HttpRequest
	:return: render
	:rtype: render
	"""
	# if not request.user.is_authenticated or 'guest' not in request.session:
	#     return redirect('index')

	try:
		file_to_be_compared_path = get_file_to_compare_path(request)
		file_to_be_compared = os.listdir(file_to_be_compared_path)
		print(file_to_be_compared)
		print('Drishyam2')
		segments = {}

		with open(os.path.join(file_to_be_compared_path, file_to_be_compared[0]), 'r') as f:
			file_to_compare_path = f.read()
			
		if os.path.exists(get_segments_path(request)):
			segment_files = os.listdir(get_segments_path(request))
			print(segment_files)
			print('Georgekutty')
			for segment_file in segment_files:
				if os.path.isfile(os.path.join(get_segments_path(request), segment_file)):
					with open(os.path.join(get_segments_path(request), segment_file), 'r') as f:
						segments[segment_file] = f.read()
						print(segments[segment_file])
						print('Fadikutty')
		file_to_compare_path_json_string = json.dumps(file_to_compare_path, cls=DjangoJSONEncoder)
		segment_json_string = json.dumps(segments, cls=DjangoJSONEncoder)
		context = {
			"fileToComparePathJsonString": file_to_compare_path_json_string,
			"segmentJsonString": segment_json_string,
		}

		return render(request, 'misconduct_detection_app/select.html', context)
	except UnicodeDecodeError:
		logger.error("Uploaded unsupported file")
		return redirect('error_uploaded_unsupported_file')


def results_index(request):
	"""The results page

	:param request: request
	:type request: HttpRequest
	:return: render
	:rtype: render
	"""
	# if not request.user.is_authenticated or 'guest' not in request.session:
	#     return redirect('index')

	# If the detection failed and there is no result, return the "no results" error page
	if not os.path.exists(get_results_path(request)):
		return redirect('error_no_results_error')

	# Read configs from disk
	configs_path_list = {}
	with open(os.path.join(get_configs_path(request), "configs.txt")) as f:
		file_lines = f.readlines()
	for line in file_lines:
		line = line.strip('\n')
		paraname, paradata = line.split(",")
		configs_path_list[paraname] = paradata

	include_segments_path = os.path.join(get_segments_path(request), "include_segments_path")
	segment_dir = os.listdir(include_segments_path)
	segment_files = {}

	for segment in segment_dir:
		if os.path.isfile(include_segments_path + "/" + segment):
			with open(include_segments_path + "/" + segment, 'r') as f:
				segment_files[segment] = f.read()

	if not configs_path_list["detectionLibSelection"] in DETECTION_LIBS.keys():
		try:
			with open(os.path.join(get_results_path(request), "results_keys.pkl"), "rb") as f:
				DETECTION_LIBS[configs_path_list["detectionLibSelection"]] = pickle.load(f)
		except FileNotFoundError:
			return redirect("error_results_keys_not_exists")

	detection_results, submission_count = DETECTION_LIBS[configs_path_list["detectionLibSelection"]].results_interpretation()

	segment_files_json_string = json.dumps(segment_files, cls=DjangoJSONEncoder)
	detection_results_json_string = json.dumps(detection_results, cls=DjangoJSONEncoder)
	# Check if uploaded file is in uploaded folder
	is_file_included = "No"
	submission_path_prefix = uploaded_file_dir_in_folder(request)
	if submission_path_prefix is not None:
		is_file_included = "Yes"

	context = {
		"ResultsJsonString": detection_results_json_string,
		"SubmissionNumber": number_of_submissions(request),
		"segmentFilesJsonString": segment_files_json_string,
		"isFileIncluded": is_file_included,
		"totalFileCount": num_external_files(request),
		"submissionPathPrefix": submission_path_prefix
	}

	return render(request, 'misconduct_detection_app/results.html', context)


# ------------------------------------Error Page Indexes------------------------------------
def error_no_results_error(request):
	return render(request, 'misconduct_detection_app/error_pages/error_no_results_error.html')


def error_uploaded_unsupported_file(request):
	context = {
		"supportedFileTypes": SUPPORTED_PROGRAMMING_LANGUAGE_EXTENSION
	}

	return render(request, 'misconduct_detection_app/error_pages/error_uploaded_unsupported_file.html', context)


def error_results_keys_not_exists(request):
	return render(request, 'misconduct_detection_app/error_pages/error_results_keys_not_exists.html')


# ------------------------------------File uploading functions------------------------------------
def upload_file(request):
	"""Single file upload function

	Accept a single file from uploading and store it.
	
	:param request: request
	:type request: HttpRequest
	:return: HttpResponse
	:rtype: HttpResponse
	"""

	if request.method == 'POST':
		handle_upload_file(request, request.FILES['file'], str(request.FILES['file']))

		# Remove the previous highlights, segments if they exist
		if os.path.exists(get_segments_path(request)):
			shutil.rmtree(get_segments_path(request))

		if os.path.exists(get_configs_path(request)):
			shutil.rmtree(get_configs_path(request))

		return HttpResponse('Uploading Success')
	else:
		return HttpResponse('Uploading Failed')


def handle_upload_file(request, file, filename):
	"""Store the file from memory to disk
	
	:param file: the file to store
	:type file: HttpRequest.FILES
	:param filename: the file name of the file
	:type filename: str
	"""

	if os.path.exists(get_file_to_compare_path(request)):
		shutil.rmtree(get_file_to_compare_path(request))
	path = get_file_to_compare_path(request)
	if not os.path.exists(path):
		os.makedirs(path)
	with open(os.path.join(path, filename), 'wb')as destination:
		for chunk in file.chunks():
			destination.write(chunk)


# ------------------------------------Folder uploading functions------------------------------------
def upload_folder(request):
	"""Folder upload function

	Accept a whole folder uploading and store the files into disk
	
	:param request: request
	:type request: HttpRequest
	:return: HttpResponse
	:rtype: HttpResponse
	"""
	if os.path.exists(get_folder_path(request)):
		# "ignore_errors=True" is used to delete read-only file
		# On Windows, the system file manager will create some read-only file which cause a problem here.
		shutil.rmtree(get_folder_path(request), ignore_errors=True)
	if request.method == 'POST':
		files = request.FILES.getlist('file')
		for f in files:
			if str(f)[0] == '.':
				# Skip UNIX/Mac hidden files
				continue
			file_name, file_extension = os.path.splitext(str(f))
			original_path = f.original_path
			handle_upload_folder(request, f, file_name, file_extension, original_path)
		return HttpResponse(number_of_submissions(request))
	else:
		return HttpResponse('Uploading Failed')


def handle_upload_folder(request, file, file_name, file_extension, original_path):
	"""Handle the folder uploading and store the files to disk
	
	:param file: one file 
	:type file: HttpRequest.FILES
	:param file_name: the name of the file
	:type file_name: str
	:param file_extension: the extension of the file
	:type file_extension: str
	:param original_path: the path of the file on client
	:type original_path: str
	"""
	path = os.path.join(get_folder_path(request), original_path)
	if not os.path.exists(path):
		os.makedirs(path)
	with open(os.path.join(path, file_name + file_extension), 'wb') as destination:
		for chunk in file.chunks():
			destination.write(chunk)


def upload_check_included(request):
	"""
	Check if the uploaded folder has the uploaded file included

	:param request:
	:return: Yes/No/NA
	"""
	if os.path.exists(get_folder_path(request)) and os.path.exists(get_file_to_compare_path(request)):
		if uploaded_file_dir_in_folder(request) is not None:
			return HttpResponse("Yes")
		else:
			return HttpResponse("No")
	else:
		return HttpResponse("NA")


def upload_update_context(request):
	"""
	Update the context of the bottom bar
	:param request:
	:return: Json formatted context
	"""
	return JsonResponse(context_processors.update_bottom_bar(request))

# ------------------------------------Examination Code------------------------------------
def examine_file(request, name):
	"""Read a file on disk and return it as plain text
	
	:param request: request
	:type request: HttpRequest
	:param name: The name of the file to show
	:type name: str
	:return: The file to show
	:rtype: HttpResponse
	"""

	try:
		path = get_file_to_compare_path(request)
		f = open(os.path.join(path, name), 'r')
		file_content = f.read()
		f.close()
		return HttpResponse(file_content, content_type="text/plain")
	except UnicodeDecodeError:
		return redirect('error_uploaded_unsupported_file')


def examine_folder(request, name):
	"""Read a file on disk and return it as plain text (for checking files
	in the uploaded folder)
	
	:param request: request
	:type request: HttpRequest
	:param name: The name of the file to show
	:type name: str
	:return: The file to show
	:rtype: HttpResponse
	"""
	try:
		path = os.path.join(get_folder_path(request), name)
		f = open(path, 'r')
		file_content = f.read()
		f.close()
		return HttpResponse(file_content, content_type="text/plain")
	except UnicodeDecodeError:
		return redirect('error_uploaded_unsupported_file')


def examine_file_in_result_page(request, name):
	"""Read detecting results pages produced by detection packages
	to the user.
	
	:param request: request
	:type request: HttpRequest
	:param name: The name of the file to show
	:type name: str
	:return: The file to show
	:rtype: HttpResponse
	"""

	path_file = os.path.join(get_results_path(request), name)
	# Here we need to deal with the possible picture files
	if ".gif" in path_file:
		image_data = open(path_file, "rb").read()
		return HttpResponse(image_data, content_type="image/png")
	else:
		f = open(path_file, 'r', encoding='iso-8859-1')
		file_content = f.read()
		f.close()
		return HttpResponse(file_content)


# ------------------------------------Select Code------------------------------------
def select_code(request):
	"""Called to save selected segments on the server
	
	:param request: request
	:type request: HttpRequest
	:return: operation state
	:rtype: HttpResponse
	"""

	if request.method == 'POST':
		if os.path.exists(get_segments_path(request)):
			shutil.rmtree(get_segments_path(request))
		try:
			os.makedirs(get_segments_path(request))
		except FileExistsError:
			pass
		print(request.POST)
		if len(request.POST) > 1:

			for code_segment in request.POST.keys():
				#print("Code Segment: " + code_segment)

				if code_segment != "csrfmiddlewaretoken":  # we don't want csrf token here
					with open(get_segments_path(request) + "/" + code_segment, 'w', newline="\n") as f:
						f.write(request.POST[code_segment])
						# file_to_be_compared_path = get_file_to_compare_path(request)
						# file_to_be_compared = os.listdir(file_to_be_compared_path)
						# with open(os.path.join(file_to_be_compared_path, file_to_be_compared[0]), 'r') as v:
						# 	file_to_compare_path = v.read()
						# f.write(file_to_compare_path)
						
						# print(request.POST[code_segment])

						# print('Sauda khara khara')
		else:
			shutil.rmtree(get_segments_path(request))
		return HttpResponse('Selection Succeeded')
	else:
		return HttpResponse('Selection Failed')


def select_check_box(request):
	"""Called to save segments including checkboxe states on the server
	
	:param request: request
	:type request: HttpRequest
	:return: operation state
	:rtype: HttpResponse
	"""

	if not os.path.exists(get_configs_path(request)):
		os.makedirs(get_configs_path(request))
	if request.method == 'POST':
		if len(request.POST) > 1:
			for checked_box in request.POST.keys():
				if checked_box != "csrfmiddlewaretoken":
					with open(get_configs_path(request) + "/" + "checked_boxes" + '.txt', 'w') as f:
						f.write(request.POST[checked_box])
		return HttpResponse('Selection Succeeded')
	else:
		return HttpResponse('Selection Failed')


def select_save_html(request):
	"""Called to save segments selection page left part in HTML format
	on the server
	
	:param request: request
	:type request: HttpRequest
	:return: operation state
	:rtype: HttpResponse
	"""
	
	if request.method == 'POST':
		try:
			os.makedirs(get_segments_path(request))
		except FileExistsError:
			pass
		if len(request.POST) > 1:
			try:
				with open(os.path.join(get_configs_path(request), "code_select_html.html"), 'w', newline='') as f:
					f.write(request.POST["codeDisplayHtml"])
			except KeyError:
				pass
		else:
			shutil.rmtree(get_segments_path(request))
		return HttpResponse('Selection Succeeded')
	else:
		return HttpResponse('Selection Failed')


def select_load_html(request):
	"""Called to load segments selection page left part in HTML format
	from the server
	
	:param request: request
	:type request: HttpRequest
	:return: the html file
	:rtype: HttpResponse
	"""
	try:
		with open(os.path.join(get_configs_path(request), "code_select_html.html"), 'r') as f:
			file_content = f.read()
			file_content_json_string = json.dumps(file_content, cls=DjangoJSONEncoder)
			return HttpResponse(file_content_json_string)
	except FileNotFoundError:
		return HttpResponse(json.dumps("FILE_NOT_FOUND", cls=DjangoJSONEncoder))

	# ------------------------------------Run detection------------------------------------
def run_detection(request):
	"""Perform detection preparation
	
	:param request: request
	:type request: HttpRequest
	:return: render
	:rtype: render
	"""

	if os.path.exists(get_results_path(request)):
		shutil.rmtree(get_results_path(request))
	return render(request, 'misconduct_detection_app/runningWaiting.html')


def run_detection_core(request):
	"""Run detection with settings
	
	Jump to the results page after detection finished
	:param request: request
	:type request: HttpRequest
	:return: render
	:rtype: render
	"""

	configs_path_list = {}
	with open(os.path.join(get_configs_path(request), "configs.txt")) as f:
		file_lines = f.readlines()
	for line in file_lines:
		line = line.strip('\n')
		paraname, paradata = line.split(",")
		configs_path_list[paraname] = paradata

	extra_settings = {}
	extra_settings["detectionLanguage"] = configs_path_list["detectionLanguage"]
	extra_settings["detectionThreshold"] = configs_path_list["detectionThreshold"]
	try:
		detection_lib = detection_libs_configs[configs_path_list["detectionLibSelection"]](request, extra_settings)
	except FileNotFoundError:
		# Detection lib initialization failed, most likely no results
		return redirect('error_no_results_error')

	detection_lib.run_without_getting_results(get_temp_working_path(request))
	
	DETECTION_LIBS[configs_path_list["detectionLibSelection"]] = detection_lib

	# If the detection failed and there is no result, return the "no results" error page
	if not os.path.exists(get_results_path(request)):
		return redirect('error_no_results_error')

	with open(os.path.join(get_results_path(request), "results_keys.pkl"), "wb") as f:
		pickle.dump(detection_lib, f)

	return redirect('results')


# ------------------------------------Some global functions------------------------------------
def clean(request):
	"""Clean the working folder of the current user
	
	:param request: request
	:type request: HttpRequest
	:return: operation state
	:rtype: HttpResponse
	"""

	file_to_compare_path = get_file_to_compare_path(request)
	results_path = get_results_path(request)
	folder_path = get_folder_path(request)
	segments_path = get_segments_path(request)
	temp_working_path = get_temp_working_path(request)
	configs_path = get_configs_path(request)

	if os.path.exists(file_to_compare_path):
		shutil.rmtree(file_to_compare_path)
	if os.path.exists(results_path):
		shutil.rmtree(results_path)
	if os.path.exists(folder_path):
		shutil.rmtree(folder_path)
	if os.path.exists(segments_path):
		shutil.rmtree(segments_path)
	if os.path.exists(temp_working_path):
		shutil.rmtree(temp_working_path)
	if os.path.exists(configs_path):
		shutil.rmtree(configs_path)

	return HttpResponse("Clean Succeeded")


def clean_session(request):
	"""Clean the user session - remove all files and remove session cookie
	
	:param request: request
	:type request: HttpRequest
	:return: operation state
	:rtype: HttpResponse
	"""

	paths_to_clear = get_session_paths(request.session)
	for path in paths_to_clear:
		if os.path.exists(path):
			shutil.rmtree(path)
	logout(request)
	
	return HttpResponse("Clean Succeeded")


def saving_configs(request):
	"""Called to save current user's configs on the server
	
	:param request: request
	:type request: HttpRequest
	:return: operation state
	:rtype: HttpResponse
	"""

	if not os.path.exists(get_configs_path(request)):
		os.makedirs(get_configs_path(request))
	if request.method == 'POST':
		if len(request.POST) > 1:
			for parameter in request.POST.keys():
				if parameter == "detectionLibSelection":
					# Clean the config file first
					with open(os.path.join(get_configs_path(request), "configs.txt"), 'w') as f:
						f.write("detectionLibSelection," + request.POST[parameter])
				else:
					with open(os.path.join(get_configs_path(request), "configs.txt"), 'a') as f:
						f.write("\n"+parameter+"," + request.POST[parameter])
		return JsonResponse({"status": "success"})
	else:
		return JsonResponse({"status": "failure"})


def auto_detect(request):
	"""Perform auto detection. Return the results to the front-end
	
	:param request: request
	:type request: HttpRequest
	:return: operation state
	:rtype: HttpResponse
	"""

	auto_detection_results = auto_detect_programming_language(request)
	auto_detection_results_json_string = json.dumps(auto_detection_results, cls=DjangoJSONEncoder)
	return HttpResponse(auto_detection_results_json_string)


def test(request):
	"""Used for testing other functions. URL has been set accordingly.

	"""

	tester = auto_detect_programming_language(request)

	return HttpResponse("test finished")

@csrf_exempt
def save_workspace(request, name):
	"""Function saves current workspace under a given name
	
	:param request: Request that has been made, with user credentials indicating 
		active session
	:type request: HttpRequest
	:param name: The desired name for the workspace
	:type name: str
	:return: Success indicator, stating if action was successful. Returns False, 
		if workspace with such name already exists
	:rtype: bool


	"""

	#TODO: Create a prompt to ask for name of the workspace
	#Check if the named workspace exists or not and if yes, delete the current and save it with the same name, if no, then ask for a name
	#Maximum sessions allowed to save = 5

	

	

	#name= 'name9'
	
	if name in list_workspaces(request):
		delete_workspace(request,name)

	if len(list_workspaces(request)) > 4:
		return False

	workspaces_path = get_workspaces_dir(request)
	ws_path = os.path.join(workspaces_path, name)
	
	os.mkdir(ws_path)
	

	paths = get_user_paths(request.user)
	
	for src, target in zip(paths, ["uploads", "reports"]):
		
		
		try:
			shutil.copytree(src, os.path.join(ws_path, target))
		except FileNotFoundError:
			pass




	return JsonResponse({'success': 'success'})

@csrf_exempt
def list_workspaces(request):
	"""Function lists all saved workspaces for logged in user
	
	:param request: Request that has been made and contains user credentials
	:type request: HttpRequest
	:return: Names of all user workspaces
	:rtype: list of str
	"""
	ws_path = get_workspaces_dir(request)

	# return JsonResponse({
	#          'success': True,
	#          'workspaces': os.listdir(ws_path)
	#      })
	return os.listdir(ws_path)

	# context = {'workspaces': os.listdir(ws_path)}

	# return render(request, 'misconduct_detection_app/sess.html',context)
	# template_name= "misconduct_detection_app/sess.html"
	# args = {}
	# text = "hello world"
	# args['mytext'] = text
	# return TemplateResponse(request, template_name, args)

@csrf_exempt
def load_workspace(request, name):
	"""Function loads a saved workspace as the active workspace. The current 
		active workspace will be overwritten without being saved before.
	
	:param request: Request that has been made and contains user credentials
	:type request: HttpRequest
	:param name: The name of the workspace to be loaded
	:type name: str
	:return: Success indicator, that indicates if action was successful. Returns 
		False, if workspace with given name does not exist
	:rtype: bool
	"""

	

	try:

		shutil.rmtree(os.path.join(APP_PATH, "uploads"))
		shutil.rmtree(os.path.join(APP_PATH, "results"))

	except FileNotFoundError:
		pass
	
	if name not in list_workspaces(request):
		
		return JsonResponse({'success': 'fail'})
	
	workspaces_path = get_workspaces_dir(request)
	ws_path = os.path.join(workspaces_path, name)

	paths = get_user_paths(request.user)
	

	for src, target in zip(["uploads", "reports"], paths):
		try:
			shutil.copytree(os.path.join(ws_path, src), target)
		except FileNotFoundError:
			pass

		
		

		#redirect to homepage

	return redirect('/')

@csrf_exempt
def delete_workspace(request, name):
	"""Function deletes a saved workspace, if such workspace exists
	
	:param request: Request that has been made and contains user credentials
	:type request: HttpRequest
	:param name: The name of the workspace to delete
	:type name: str
	"""
	workspaces_path = get_workspaces_dir(request)
	ws_path = os.path.join(workspaces_path, name)
	
	if os.path.exists(ws_path):
		shutil.rmtree(ws_path)


def list_workspace(request):
	"""Function deletes a saved workspace, if such workspace exists
	
	:param request: Request that has been made and contains user credentials
	:type request: HttpRequest
	:param name: The name of the workspace to delete
	:type name: str
	"""
	# return JsonResponse({ 'success': True, 'workspaces': list_workspaces(request) })
	return render(request, 'misconduct_detection_app/sess.html', context = {"user_workspaces": list_workspaces(request)})

@csrf_exempt
def select_code_moss(request):
	"""Called to run as MOSS mode
	
	:param request: request
	:type request: HttpRequest
	:return: operation state
	:rtype: HttpResponse
	"""
		
		
	

	if request.method == 'POST':
		if os.path.exists(get_segments_path(request)):
			print('YOLOOOSHOLOO1')
			shutil.rmtree(get_segments_path(request))
		try:
			os.makedirs(get_segments_path(request))
		except FileExistsError:
			pass
		print(request.POST)

		with open(get_configs_path(request) + "/" + "checked_boxes" + '.txt', 'w') as f:
			f.write('1')



		code_segment = "Segment_1"

		with open(get_segments_path(request) + "/" + code_segment, 'w', newline="\n") as f:
						#f.write(request.POST[code_segment])
			file_to_be_compared_path = get_file_to_compare_path(request)
			file_to_be_compared = os.listdir(file_to_be_compared_path)
			with open(os.path.join(file_to_be_compared_path, file_to_be_compared[0]), 'r') as v:
				file_to_compare_path = v.read()
				f.write(file_to_compare_path)
				

		with open(get_configs_path(request) + "/" + "checked_boxes" + '.txt', 'r') as e:
			checked_segments = e.read()


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




		

		# if len(request.POST) > 1:
		# 	print('YOLOOOSHOLOO')
		# 	for code_segment in request.POST.keys():
		# 		print('YOLOOOSHOLOO')

		# 		if code_segment != "csrfmiddlewaretoken":  # we don't want csrf token here

		
			
						
						# print(request.POST[code_segment])

						# print('Sauda khara khara')
		# else:
		# 	print('YOLOOOSHOLOO3')
		# 	shutil.rmtree(get_segments_path(request))
		#return HttpResponse('Selection Succeeded')
		return HttpResponse('Selection Succeeded')
	else:
		return HttpResponse('Selection Failed')

