#!/bin/bash
start_gaea(){
	cd ${PWD}/ts-build && node app.js
}

start_remidner(){
	cd ${PWD}/ts-build && node app.remidner.js
}

start_fetch_reminder(){
	cd ${PWD}/ts-build && app.fetch.reminder.js
}

main(){
	case $1 in
		gaea)
			start_gaea
			;;
		remidner)
			start_remidner
			;;
		fetch_start_remidner)
			start_fetch_reminder
			;;
		*)
			echo "-----------"
			;;
	esac
}
main $1
