#!/usr/bin/env bash
echo "==================================================================="
echo "= Welcome to the Misconduct Assessment Tool Quick Install Script! ="
echo "==================================================================="
echo "Install Miniconda3? [Y,n]"
read input
if [[ $input == "Y" || $input == "y" ]]; then
    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash Miniconda3-latest-Linux-x86_64.sh

    rm Miniconda3-latest-Linux-x86_64.sh
    echo "export PATH=\""\$PATH":$HOME/miniconda3/bin\"" >> ~/.benv
    source ~/.benv
else
        echo "Skipping Conda installation"
fi

conda_root="$HOME/miniconda3/envs/mat"
echo "Creating virtual environment"
conda env create -f environment.yml
conda activate mat

echo "Virtual environment path:"
echo $conda_root

cd ..
install_pos="$(pwd)"
echo "Your installation path is:"
echo $install_pos

cd $conda_root

mkdir -p ./etc/conda/activate.d
mkdir -p ./etc/conda/deactivate.d

echo -e '#!/bin/sh\n' >> ./etc/conda/activate.d/env_vars.sh
echo "Enter the value for the SECRET_KEY environment variable:"
read secret
echo "export SECRET_KEY=$secret" >> ./etc/conda/activate.d/env_vars.sh
echo -e '#!/bin/sh\n' >> ./etc/conda/deactivate.d/env_vars.sh
echo 'unset SECRET_KEY' >> ./etc/conda/deactivate.d/env_vars.sh

source conda deactivate
source conda activate mat

cd $install_pos

python manage.py migrate

echo "==================================================================="
echo "Installation finished!"
echo "Activate the virtual environment: $ source activate mat"
echo "Run the system: $ python manage.py runserver"
echo "==================================================================="
