# TSIM-based Fault Injection Attack and Countermeasures

**SETUP:**

1. Download and install Oracle VM VirtualBox 6.1.32 binary for your current operating system.
2. Download Ubuntu 20.04.3 LTS image and install it on a VirtualBox with 32G drive and 4G RAM configuration. 
3. To download git repostory:
   > sudo apt install subversion <br/>
   > svn co https://github.com/richa-design/TSIM-Based-Fault-Injection-Attack-and-Countermeasures
4. To configure python packages:
   > sudo apt update <br/>
   > sudo apt install python3-pip <br/>
   > sudo apt install python-apt <br/>
   > cd TSIM-Based-Fault-Injection-Attack-and-Countermeasures/FIA_Demos/software <br/>
   > pip3 install -r requirements.txt <br/>
   > cd ../../..
5. Setup TSIM-LEON3 simulator, an Instruction-Level Simulator for Leon-based systems, used for fault injection simulation.
   > cd TSIM-Based-Fault-Injection-Attack-and-Countermeasures/FIA_Demos/software <br/>
   > sudo cp -rp tsim-eval /opt <br/>
   > cd ../../..
6. Setup leon3 cross-compiler
   > wget https://www.gaisler.com/anonftp/bcc2/bin/bcc-2.2.0-gcc-linux64.tar.xz <br/>
   > sudo tar -xJf bcc-2.2.0-gcc-linux64.tar.xz -C /opt/ 
7. To be able to run TSIM-LEON3, install libncurses5 package:
   > sudo apt-get install libncurses5 
8. Setup path (don't forget to add these to ~/.bashrc as well)
   > export PATH=/opt/bcc-2.2.0-gcc/bin/:$PATH <br/>
   > export PATH=$PATH:$HOME/.local/bin <br/>
   > export PATH=/opt/tsim-eval/tsim/linux-x64/:$PATH 
9. To start jupyter notebook:
   > cd TSIM-Based-Fault-Injection-Attack-and-Countermeasures/FIA_Demos/tutorials <br/>
   > jupyter notebook <br/>
   > open Getting Started.ipynb
