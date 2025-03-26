#В файле /etc/sudoers добавить строчку
#www-data    ALL=(ALL) NOPASSWD:ALL

www-data    ALL=(ALL) NOPASSWD: /usr/bin/htpasswd
