#bin/bash

#echo -e "$1\n$2\n$3\n" | passwd $4

echo -e "$1\n$2\n" | /usr/bin/sudo passwd $3
