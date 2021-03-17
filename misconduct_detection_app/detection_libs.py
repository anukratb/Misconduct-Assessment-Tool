import os
import shutil
from bs4 import BeautifulSoup
import bs4
import pickle
import subprocess

import logging

logger = logging.getLogger(__name__)


class DetectionLib:
    """General detection library."""

    def __init__(self, name, lib_path, results_path, segments_path, folder_to_compare_path):
        """Create a new detection library object.
        
        :param name: the name of this library
        :type name: str
        :param lib_path: the path of the library on the server
        :type lib_path: str
        :param results_path: the path to store produced results. The results format should be:
        (results, submission_number), where results should be a dict which contains the results
        and file relations. And the submission_number should be the number of submissions rather
        than the number of files.
        :type results_path: str
        :param segments_path: the path where stores the uploaded single file
        :type segments_path: str
        :param folder_to_compare_path: the path where the uploaded folder is stored
        :type folder_to_compare_path: str
        """

        self.name = name
        self.lib_path = lib_path
        self.results_path = results_path
        self.segments_path = segments_path
        self.folder_to_compare_path = folder_to_compare_path
        self.file_language_supported = []

        self.MINIMUM_SIZE_SEGMENT = 5
        # Length of segment lower bound needed because of the sensitivity of Detection Libraries

    def __str__(self):
        """ String represantation """
        return "<%s> DetectionLib".format(self.name)

    def get_results(self, temp_working_path):
        """Run the detection by the current library on given temp_working_path
        
        :param temp_working_path: the path where to run the detection library
        :type temp_working_path: str
        :return: the results produced by the detection library. BE AWARE:
        :rtype: [type]
        """

        assert (len(self.file_language_supported) != 0), "No support language defined for " + self.name
        self.run_detection(temp_working_path=temp_working_path)
        results = self.results_interpretation()
        self.clean_working_envs(temp_working_path=temp_working_path)
        return results

    def run_without_getting_results(self, temp_working_path):
        """Run the detection by the current library on given temp_working_path without returning the results
        
        :param temp_working_path: the path where to run the detection library
        :type temp_working_path: str
        """

        assert (len(self.file_language_supported) != 0), "No support language defined for " + self.name
        self.run_detection(temp_working_path=temp_working_path)
        self.clean_working_envs(temp_working_path=temp_working_path)

    def run_detection(self, temp_working_path):
        """Virtual function. Run the misconduct detection.
        
        :param temp_working_path: the temp working folder path
        :type temp_working_path: str
        """

        raise NotImplementedError

    def results_interpretation(self):
        """Virtual function. Interpret the results produced by this detection 
        package. It should return a tuple (results, submission_number). The 
        results should be a dict which uses the segment file names as keys. Its
        values should be the similarity and a list contains similar file links.
        
        """

        raise NotImplementedError

    def clean_working_envs(self, temp_working_path):
        """Virtual function. Clean the working folder.
        
        :param temp_working_path: the temp working folder path
        :type temp_working_path: str
        """

        raise NotImplementedError

    # To improve the code readability, following getters setters will not contain comments.
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def lib_path(self):
        return self.__lib_path

    @lib_path.setter
    def lib_path(self, lib_path):
        if os.path.isfile(lib_path):
            self.__lib_path = lib_path
        else:
            raise FileNotFoundError("The library given is not found")

    @property
    def results_path(self):
        return self.__results_path

    @results_path.setter
    def results_path(self, results_path):
        self.__results_path = results_path

    @property
    def segments_path(self):
        return self.__file_to_compare_path

    @segments_path.setter
    def segments_path(self, file_to_compare_path):
        self.__file_to_compare_path = file_to_compare_path

    @property
    def folder_to_compare_path(self):
        return self.__folder_to_compare_path

    @folder_to_compare_path.setter
    def folder_to_compare_path(self, folder_to_compare_path):
        self.__folder_to_compare_path = folder_to_compare_path

    @property
    def file_language_supported(self):
        return self.__file_language_supported

    @file_language_supported.setter
    def file_language_supported(self, file_language_supported):
        self.__file_language_supported = file_language_supported


def file_lines(file_path):
    """Counts the non blank lines in a file that start with alpha characters (no comments)
    (good enough estimate of token size for sensitivity parameter
    assuming that a line contains at least one instruction)

    :param file_path: Path of the segment
    :return: number of non blank lines
    """
    line_count = 0

    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if line and line[0].isalpha():
                line_count += 1

    return line_count


class Jplag(DetectionLib):
    """JPlag detection library."""

    def __init__(self, lib_path, results_path, segments_path, folder_to_compare_path, file_language, threshold,
                 name="JPlag"):
        """Create a new JPlag detection package wrapper object.

        :param name: the name of this library
        :type name: str
        :param lib_path: the path of the library on the server
        :type lib_path: str
        :param results_path: the path to store produced results. The results format should be:
        (results, submission_number), where results should be a dict which contains the results
        and file relations. And the submission_number should be the number of submissions rather
        than the number of files.
        :type results_path: str
        :param segments_path: the path where stores the uploaded single file
        :type segments_path: str
        :param folder_to_compare_path: the path where sotres the uploaded folder
        :type folder_to_compare_path: str
        ----------------------Only for JPlag----------------------
        :param file_language: which languages are supported by this detection package
        :type file_language: str
        :param number_of_matches: (Matches) Number of matches that will be saved. This can be
        set with either a number or a percentage. I would suggest to set it with a percentage.
        The JPlag will only show the results with similarity higher than this number.
        :type number_of_matches: str
        """

        super().__init__(name, lib_path, results_path, segments_path, folder_to_compare_path)
        self.file_language_supported = ["java17", "python3", "c/c++",
                                        "c#-1.2", "char", "text", "scheme"]
        assert (file_language in self.file_language_supported), "Language parameter {0} not supported by JPlag".format(
            file_language)
        self.file_language = file_language
        self.threshold = threshold
        self.file_relation = {}
        self.NORMAL_SIZE_SEGMENT = 12
        self.optimized = False
        logger.debug('New instance of %s', self.name)

    def run_detection(self, temp_working_path):
        """Run the detection with given settings using OS command.
        
        :param temp_working_path: the temp working folder path
        :type temp_working_path: str
        """
        self.run_detection_optimized(temp_working_path)
        return


    def run_detection_optimized(self, temp_working_path):
        """Run the detection with optimized sensitivity parameters

        :param temp_working_path: the temp working folder path
        :type temp_working_path: str
        """
        logger.debug('Running detection on working environment %s', temp_working_path)

        small_counter = 0
        normal_counter = 0

        # Preparing files
        if not os.path.exists(temp_working_path):
            os.makedirs(temp_working_path)
        else:
            logger.critical("Temp working path not empty! <{0}>".format(temp_working_path))

        small_files = []
        normal_files = []

        for file_name in os.listdir(self.segments_path):
            current_file = os.path.join(self.segments_path, file_name)
            file_size = file_lines(current_file)
            if file_size < self.NORMAL_SIZE_SEGMENT:
                # Segment is small size
                small_counter += 1
                small_files.append(file_name)
            else:
                # Segment is normal size
                normal_counter += 1
                normal_files.append(file_name)
            shutil.copy(current_file, os.path.join(temp_working_path, file_name))

        counter = 0
        for (dir_path, dir_names, file_names) in os.walk(self.folder_to_compare_path):
            for file_name in file_names:
                if not os.path.exists(temp_working_path + file_name):
                    self.file_relation[str(counter)] = os.path.join(dir_path, file_name)
                    shutil.copy(self.file_relation[str(counter)],
                                temp_working_path + "/" + str(counter) + "_" + file_name)
                    counter += 1

        # HACK: Please notice here, you shall never allow users to run code on your server directly.
        # Try only receive part parameters from users, such as what I did here. DO NOT let users run
        # their command directly, that would be very dangerous.

        if small_counter > 0:
            self.optimized = True

            # First check the smaller segments
            os.system("java -jar {0} -t 3 -l {1} -m {2}% -r {3} {4}".format(self.lib_path,
                                                                    self.file_language,
                                                                    self.threshold,
                                                                    os.path.join(self.results_path, "small"),
                                                                    temp_working_path))

            # Then check the normal segments
            os.system("java -jar {0} -t 6 -l {1} -m {2}% -r {3} {4}".format(self.lib_path,
                                                                            self.file_language,
                                                                            self.threshold,
                                                                            os.path.join(self.results_path, "normal"),
                                                                            temp_working_path))

            # Save which segments are small and which normal size
            with open(os.path.join(self.results_path, 'optimized_files.pkl'), 'wb') as f:
                pickle.dump([small_files, normal_files], f)

        else:
            os.system("java -jar {0} -l {1} -m {2}% -r {3} {4}".format(self.lib_path,
                                                                       self.file_language,
                                                                       self.threshold,
                                                                       self.results_path,
                                                                       temp_working_path))

    def results_interpretation(self):
        """Interpret the results produced by JPlag.
        
        :return: (results, submission_number). The results should be a dict which
        uses the segment file names as keys. Its values should be the similarity
        and a list contains similar file links.
        :rtype: (dict, int)
        """

        def process_result_file(result_path, file_relation, search_files, path_folder=""):
            # Inner function that processes the html result file
            with open(result_path, encoding='iso-8859-1') as fp:
                soup = BeautifulSoup(fp, 'html.parser')

            # search_files = os.listdir(segments_path)
            for i in range(len(search_files)):
                search_files[i] = search_files[i][:search_files[i].find(".")]

            results_file = {}

            for search_file in search_files:
                temp_similarities_for_searching_file = {}
                for tag in soup.find_all('h4'):
                    if 'Matches sorted by maximum similarity (' in tag.contents:
                        for tr_tag in tag.parent.find_all('tr'):
                            if search_file in tr_tag.contents[0].contents[0]:
                                similarities = tr_tag.contents[2:]
                                for one_similarity in similarities:
                                    original_file_name = one_similarity.contents[0].contents[0]
                                    if "Segment_" in original_file_name:
                                        # matched with another segment edge case
                                        continue
                                    print('filename a full ', original_file_name)
                                    original_result_link = one_similarity.contents[0].get("href")
                                    similarity = one_similarity.contents[2].contents[0]
                                    temp_similarities_for_searching_file[
                                        file_relation[original_file_name[:original_file_name.find("_")]]] = [
                                        similarity, os.path.join(path_folder, original_result_link)]

                        for td_tag in tag.parent.find_all('td'):
                            for element in td_tag.contents:
                                if isinstance(element, bs4.element.Tag):
                                    if len(element.contents) > 0:
                                        if search_file in element.contents[0]:
                                            original_file_name = td_tag.parent.contents[0].contents[0]
                                            if "Segment_" in original_file_name:
                                                # matched with another segment edge case
                                                continue
                                            original_result_link = td_tag.contents[0].get("href")
                                            similarity = td_tag.contents[2].contents[0]
                                            print('path_folder = ', path_folder)
                                            print('filename ', original_file_name[:original_file_name.find("_")])
                                            temp_similarities_for_searching_file[
                                                file_relation[original_file_name[:original_file_name.find("_")]]] = [
                                                similarity, os.path.join(path_folder, original_result_link)]

                results_file[search_file] = temp_similarities_for_searching_file
            return results_file

        # Change this to change how to define a "submission" in the source folder
        # This line only list the sub-level folders in the source folder
        number_of_submissions = len(os.listdir(
            os.path.join(self.folder_to_compare_path, os.listdir(self.folder_to_compare_path)[0])))
        logger.info("Submission number:", number_of_submissions)

        if self.optimized:
            with open(os.path.join(self.results_path, 'optimized_files.pkl'), 'rb') as f:
                small_files, normal_files = pickle.load(f)

            results_small = process_result_file(
                os.path.join(self.results_path, "small", "index.html"),
                file_relation=self.file_relation, search_files=small_files, path_folder="small")
            results_normal = process_result_file(
                os.path.join(self.results_path, "normal", "index.html"),
                file_relation=self.file_relation, search_files=normal_files, path_folder="normal")
            results = {**results_small, **results_normal}
        else:
            results = process_result_file(os.path.join(self.results_path, "index.html"),
                                          file_relation=self.file_relation,
                                          search_files=os.listdir(self.segments_path))

        return results, number_of_submissions

    def clean_working_envs(self, temp_working_path):
        """Delete temp working folder
        
        :param temp_working_path: the temp working folder path
        :type temp_working_path: str
        """
        logger.debug('Cleaning working environment %s', temp_working_path)
        shutil.rmtree(temp_working_path)

    # To improve the code readability, following getters setters will not contain comments.
    @property
    def file_language(self):
        return self.__file_language

    @file_language.setter
    def file_language(self, file_language):
        if file_language not in self.file_language_supported:
            raise TypeError("Following language type is not supported by Jplag: " + file_language)
        self.__file_language = file_language

    @property
    def number_of_matches(self):
        return self.__number_of_matches

    @number_of_matches.setter
    def number_of_matches(self, number_of_matches):
        self.__number_of_matches = number_of_matches


class SID(DetectionLib):
    """SID detection library."""

    def __init__(self, results_path, segments_path, folder_to_compare_path, file_language, 
                 lib_path=None, name="SID", threshold=80):
        """Create a new SID detection package wrapper object.
        
        :param name: the name of this library
        :type name: str
        :param lib_path: the path of the library on the server
        :type lib_path: str
        :param results_path: the path to store produced results. The results format should be:
        (results, submission_number), where results should be a dict which contains the results
        and file relations. And the submission_number should be the number of submissions rather
        than the number of files.
        :type results_path: str
        :param segments_path: the path where stores the uploaded single file
        :type segments_path: str
        :param folder_to_compare_path: the path where the uploaded folder is stored
        :type folder_to_compare_path: str
        ----------------------Only for SID----------------------
        :param file_language: which languages are supported by this detection package
        :type file_language: str
        :param threshold: Minimum similarity percent to be reported
        :type threshold: int
        """

        super().__init__(name, lib_path, results_path, segments_path, folder_to_compare_path)
        self.file_language_supported = ["python3", "matlab"]
        assert (file_language in self.file_language_supported), "Language parameter {0} not supported by SID".format(
            file_language)
        self.file_language = file_language
        self.threshold = threshold
        self.NORMAL_SIZE_SEGMENT = 12
        logger.debug('New instance of %s', self.name)


    def run_detection(self, temp_working_path):
        """Run the detection with optimized sensitivity parameters

        :param temp_working_path: the temp working folder path
        :type temp_working_path: str
        """
        logger.debug('Running detection on working environment %s', temp_working_path)

        # Preparing files
        if not os.path.exists(temp_working_path):
            os.makedirs(temp_working_path)
            os.makedirs(os.path.join(temp_working_path, "small"))
            os.makedirs(os.path.join(temp_working_path, "normal"))
            os.makedirs(os.path.join(temp_working_path, "all_submissions"))
            os.makedirs(os.path.join(self.results_path, "small"))
            os.makedirs(os.path.join(self.results_path, "normal"))
        else:
            logger.critical("Temp working path not empty! <{0}>".format(temp_working_path))

        small_files = []
        normal_files = []
        all_submission_files = []

        for file_name in os.listdir(self.segments_path):
            current_file = os.path.join(self.segments_path, file_name)
            file_size = file_lines(current_file)
            if file_size < self.NORMAL_SIZE_SEGMENT:
                # Segment is small size
                small_files.append(current_file)
                shutil.copy(current_file, os.path.join(temp_working_path, "small", file_name))
            else:
                # Segment is normal size
                normal_files.append(current_file)
                shutil.copy(current_file, os.path.join(temp_working_path, "normal", file_name))

        counter = 0
        for (dir_path, _, file_names) in os.walk(self.folder_to_compare_path):
            for file_name in file_names:
                current_file = os.path.join(dir_path, file_name)
                all_submission_files.append(current_file)
                if not os.path.exists(temp_working_path + file_name):
                    shutil.copy(current_file,
                                os.path.join(temp_working_path, "all_submissions", str(counter) + "_" + file_name))
                    counter += 1

        # HACK: Please notice here, you shall never allow users to run code on your server directly.
        # Try only receive part parameters from users, such as what I did here. DO NOT let users run
        # their command directly, that would be very dangerous.

        if len(small_files) > 0:
            # First check the smaller segments
            with open(os.path.join(self.results_path, "small", "result.json"), 'w') as f:
                cmd = ['sid compare', '-s', '4', '-w', '4', '-l', self.file_language, 
                    '-vv', '--output', os.path.join(self.results_path, "small")]
                for file in all_submission_files + small_files: 
                    cmd += ['-f', "'{}'".format(file)]
                proc = subprocess.Popen(" ".join(cmd), shell=True, stdout=f)
                proc.wait()

        with open(os.path.join(self.results_path, "normal", "result.json"), 'w') as f:
            cmd = ['sid compare', '-s', '6', '-w', '10', '-l', self.file_language,
                '-vv', '--output', os.path.join(self.results_path, "normal")]
            for file in all_submission_files + normal_files: 
                cmd += ['-f', "'{}'".format(file)]
            proc = subprocess.Popen(" ".join(cmd), shell=True, stdout=f)
            proc.wait()

        with open(os.path.join(self.results_path, 'optimized_files.pkl'), 'wb') as f:
            pickle.dump([small_files, normal_files], f)


    def results_interpretation(self):
        """Method interprets the results produced by SID.
        
        :return: (results, submission_number). The results should be a dict which
        uses the segment file names as keys. Its values should be the similarity
        and a list contains similar file links.
        :rtype: (dict, int)
        """
        number_of_submissions = len(os.listdir(
            os.path.join(self.folder_to_compare_path, os.listdir(self.folder_to_compare_path)[0])))
        logger.info("Submission number:", number_of_submissions)

        with open(os.path.join(self.results_path, 'optimized_files.pkl'), 'rb') as f:
            small_files, normal_files = pickle.load(f)

        small_results = self.parse_result_files("small", small_files)
        normal_results = self.parse_result_files("normal", normal_files)

        results = {**small_results, **normal_results}

        return results, number_of_submissions


    def parse_result_files(self, subdir, segment_names):
        """Method traverses a directory of HTML result files to locate any 
            result files and parses these files. Overall similarity percentage, 
            as well as the path to full report is extracted from the HTML report
        
        :param subdir: Directory, under results path, which to traverse in order 
            to find all results. Results are divided in subdirectories to 
            accommodate different length of files
        :type subdir: str
        :param segment_names: List of segment names that are in the current 
            detection category. This is used to determine if the current result 
            file corresponds to the segment we are interested in
        :type segment_names: list of str
        :return: (results, submission_number). The results should be a dict 
            which uses the segment file names as keys. Its values should be the 
            similarity and a list contains similar file links.
        :rtype: (dict, int)
        """
        sources = {}

        for segment in segment_names:
            segment_name = self.get_segment_name(segment)
            sources[segment_name] = {}

        files = os.listdir(os.path.join(self.results_path, subdir))
        for file in files:
            with open(os.path.join(self.results_path, subdir, file)) as fp:
                soup = BeautifulSoup(fp, 'html.parser')
            
            file_results = soup.find(id='targetFile')
            filename = file_results.find(class_='name')
            if filename.contents[0] not in segment_names:
                continue

            remote_file = soup.find(id='sourceFile')
            remote_filename = remote_file.find(class_='name').contents[0]
            similarity = file_results.find(class_='similarity').contents[0]

            if os.path.dirname(remote_filename) == self.segments_path:
                # Exclude cross-segment matches
                continue

            similarity_parsed = float(similarity.strip().strip("%"))
            if similarity_parsed < self.threshold:
                # Exclude mathces with too little similarity
                continue

            segment_name = self.get_segment_name(filename.contents[0])
            sources[segment_name][remote_filename] = [
                similarity.strip(), 
                os.path.join(subdir, file)
            ]

        return sources


    def get_segment_name(self, full_path):
        """Method parses full filepath and returns the name of the file without 
            the file extension
        
        :param full_path: Full file path
        :type full_path: str
        :return: Name of the file without the extension
        :rtype: str
        """
        filename = os.path.basename(full_path)
        return filename[:filename.rfind(".")]


    def clean_working_envs(self, temp_working_path):
        """Delete temp working folder
        
        :param temp_working_path: the temp working folder path
        :type temp_working_path: str
        """
        logger.debug('Cleaning working environment %s', temp_working_path)
        shutil.rmtree(temp_working_path)


    # To improve the code readability, following getters setters will not contain comments.
    @property
    def file_language(self):
        return self.__file_language


    @file_language.setter
    def file_language(self, file_language):
        if file_language not in self.file_language_supported:
            raise TypeError("Following language type is not supported by SID: " + file_language)
        self.__file_language = file_language


    @property
    def lib_path(self):
        return self.__lib_path


    @lib_path.setter
    def lib_path(self, lib_path):
        # There is no file for SID, lib_path variable is not used in this class
        # but required by parent class hence the empty setter
        self.__lib_path = lib_path

