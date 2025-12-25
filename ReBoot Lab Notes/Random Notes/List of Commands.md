**Update** 
sudo apt update && sudo apt upgrade -y      = ALL


**Pi Info** 
sudo raspi-config

**NETWORK**

ping MasterTOOL-DiagTool0 -c 2
ping MasterHelper -c 2
ping MasterGuard -c 2
ping RBL-SurfaceHub -c 2

CleanUP
sudo apt clean
sudo apt autoclean
sudo apt autoremove --purge

Memory cache CleanUP
sync
echo 3 | sudo tee /proc/sys/vm/drop_caches

Safe CleanUp Combot = All 
sudo apt autoremove --purge -y && sudo apt clean && sync && echo 3 | sudo tee /proc/sys/vm/drop_caches

SAVE WORK IN AI TEAM:
Type save:project_name

