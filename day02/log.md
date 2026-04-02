This is log for day 02 learning


Command: ' ls -ls folder/file_name' gives permission status of the target
- rw- r-- r--
│ │   │   │
│ │   │   └── Others: read only
│ │   └──── Group: read only
│ └──────── Owner: read + write
└────────── file type: - means file, d means directory

Octal number system is used to decode the file permission
Read r 4 
Write w 2 
Execute x 1 
None - 0

(Eg. rwx = 7, r-x = 5, -wx = 3)


sudo = SuperUserDO

