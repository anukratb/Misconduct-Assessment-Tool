# Misconduct Assessment Tool (*MAT*)	![license](https://badgen.now.sh/badge/license/GPL-3.0/blue)

> Tool for accessing academic miscoduct

The aim of this tool is to test student submissions that are not obvious cases, but suspected of misconduct due to multiple small segments
being similar to other submissions. With a large number of submissions, it is fairly likely that some segments will be similar by chance. This tool
is used to help in such situations, by estimating the expected number of submissions with that exact combination of segments. It is built to assist
the decision making process, it does not replace it.

For each suspect segment, the individual probability of that segment is calculated by taking the number of submissions that have a similar
segment over the number of all the submissions. Segments that are present in a lot of submissions have a higher individual probability. The joint
probability is then calculated by assuming that each segment is independent and taking the product of all the segments' individual probabilities.
Finally, to calculate the estimated number of submissions we take the joint probability and multiply it with the number of all the submissions. The
resulting number should be the number of students anticipated to have the exact combination of the suspected segments. If the expected
number is lower than one, a case of misconduct is suggested. Please note that the results are not conclusive.


## Requirements

> `Java` SE Runtime Environment(JRE) >= 1.8.0

### Optional
> `Anaconda` >= 5.2 **OR** `Miniconda` >= 4.5.4

Otherwise, install the required `Python` dependencies listed in ``environment.yml`` using `pip` manually and skip the the installation guide below

## Development Installation

1. Clone the repository
```sh
git clone https://github.com/iamstelios/Misconduct-Assessment-Tool
```

2. Create the conda environment:
```sh
cd Misconduct-Assessment-Tool/scripts/
conda env create -f environment.yml
cd ..
```

3. Activate the environment

OS X & Linux:
```sh
conda activate mat
```
Windows:
```sh
activate mat
```

> Note that the system requires an environment variable ``SECRET_KEY`` to be set

4. Follow the link below for instruction of how to include the ``SECRET_KEY`` environment variable in your conda environment.
<https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#saving-environment-variables>

## Clearing user sessions

Django does not ship with built in concurrency mechanisms or asynchronous task execution, thus sessions must be cleaned manually. On production environment that is done by a cronjob running [`clearsessions` command](https://docs.djangoproject.com/en/2.0/ref/django-admin/#django-admin-clearsessions).

## Running the Misconduct Assessment Tool

1. Apply the database migrations (only when the database model structure is modified and during the first run)
```sh
python manage.py migrate
```

2. Run the server!
```sh
python manage.py runserver <optional ip:port>
```

## Screens
 
#### Welcome Page
![Welcome Page](https://github.com/iamstelios/Misconduct-Assessment-Tool/blob/master/screens/welcome_page.png?raw=true)

#### Upload Page
![Upload Page](https://github.com/iamstelios/Misconduct-Assessment-Tool/blob/master/screens/upload_page.png?raw=true)

#### Segment Selection Page
![Segment Selection Page](https://github.com/iamstelios/Misconduct-Assessment-Tool/blob/master/screens/segments_selection_page.png?raw=true)

#### Results Page
![Results Page](https://github.com/iamstelios/Misconduct-Assessment-Tool/blob/master/screens/results_page.png?raw=true)


## Meta

*Stelios Milisavljevic* – [https://iamstelios.com](https://iamStelios.com) – [https://github.com/iamstelios](https://github.com/iamstelios)

Distributed under the GNU General Public License. See ``LICENSE`` for more information.

Final year project UG4 *BEng Software Engineering*

Supervised by *Prof. Kyriakos Kalorkoti*, School of Informatics, University of Edinburgh

System inherited from *Yuechen Xie* – <https://github.com/Weak-Chicken/misconduct_detection_project>

## Contributing

1. Fork it (<https://github.com/iamstelios/Misconduct-Assessment-Tool>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

