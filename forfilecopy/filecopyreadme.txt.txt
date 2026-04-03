1) 6senderfolder.py should be in sender system ofc
-> In this file change the following 
a) Update FOLDER_TO_SEND = r"C:\emahe\1A_pythonangela\1_Python_HelloWorld-utilities\utlities_Sep17_2025" 
 -> to the folder which you want to send 
 
b) Update  TARGET_IP = "192.168.0.109" to the hm system ip 
2) 6foldereceiver.py should be in receiving system hme
-> no file change needed

3) Once changes are done :
a) run 6foldereceiver.py -> allow firewall access 
b) run 6senderfolder.py -> which will receive files to downloads folder 

4) No allow firewall access needed for system which runs 6senderfolder.py
                      