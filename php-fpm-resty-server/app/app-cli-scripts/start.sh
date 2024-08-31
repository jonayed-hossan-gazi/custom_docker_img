#!/bin/bash

# Load Server Template
if [ ! -z "$STATIC_SERVER" ]; then
 cp -vf /var/www/app-conf/nginx-static-server.conf /etc/nginx/conf.d/default.conf
elif [ ! -z "$LUA_SERVER" ]; then
 cp -vf /var/www/app-conf/nginx-lua-server.conf /etc/nginx/conf.d/default.conf
else
 cp -vf /var/www/app-conf/nginx-server.conf /etc/nginx/conf.d/default.conf
fi

# Set custom webroot
if [ ! -z "$WEBROOT" ]; then
 sed -i "s#root /var/www/app/public;#root ${WEBROOT};#g" /etc/nginx/conf.d/default.conf
fi

#file="extra.sh"

# Start supervisord and services
exec /usr/bin/supervisord -n -c /etc/supervisord.conf
