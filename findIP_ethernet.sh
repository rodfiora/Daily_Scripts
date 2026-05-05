#!/bin/bash

echo "--------------HR PORTS--------------"
networksetup -listallhardwareports

echo "--------------CHECK PORTS--------------"
for ((i=0; i<5; i++))
	do
		IP=$(ipconfig getifaddr en$i)
		if [ -n "$IP" ]; then
			echo -e "\033[32mIP en$i: $IP\033[0m"    # green if connected
		else
			echo -e "\033[31mIP en$i: not connected\033[0m"    # red if not
		fi
	done

IP=$(ipconfig getifaddr en7)
if [ -n "$IP" ]; then
	echo -e "\033[32mIP en7: $IP\033[0m"    # green if connected
else
	echo -e "\033[31mIP en7: not connected\033[0m"    # red if not
fi
