# TSIM-based Fault Injection Attack and Countermeasures

**SETUP:**

1. Download and install Oracle VM VirtualBox 6.1.32 binary for your current operating system.
2. Download Ubuntu 20.04.3 LTS image and configure VirtualBox with this image. 
3. Run below commands in terminal to clone git repostory containing source code:
   > sudo apt install git <br/>
   > git clone <this repository url>
4. To install pip for Python3(version 3.8.10 installed by default on Ubuntu 20.04.3), run the following commands in the terminal:
   > sudo apt update <br/>
   > sudo apt install python3-pip
5. requirements.txt file should list all Python libraries that our notebooks depend on, and they will be installed using:
   > cd FIA_Demos/software <br/>
   > pip3 install -r requirements_test.txt
6. To be able to run jupyter notebook from terminal, you need to make sure that $HOME/.local/bin is in your path. Do this by adding the following line to the end of ~/.bashrc file and then close the terminal:
   > export PATH=$PATH:$HOME/.local/bin
7. To be able to run TSIM-LEON3, Instruction Level Simulation for Leon-based systems, used for fault injection simulation, install the required package by running the following command in the terminal:
   > sudo apt-get install libncurses5  
8. To get started with the tutorial, run the following commands in the terminal:
   > cd FIA_Demos/tutorials <br/>
   > jupyter notebook <br/>
   > open Getting Started.ipynb
