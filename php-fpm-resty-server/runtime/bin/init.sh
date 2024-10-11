#!/bin/bash

cp -vf /var/www/runtime/conf/supervisord.conf /etc/supervisord.conf
cp -vf /var/www/runtime/conf/nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
cp -vf /var/www/runtime/conf/php-fpm.conf /usr/local/etc/php-fpm.conf
cp -vf /var/www/runtime/conf/php-fpm-pool.conf /usr/local/etc/php-fpm.d/www.conf
cp -vf /var/www/runtime/conf/php-custom-ini.conf /usr/local/etc/php/conf.d/php-custom.ini

# Load Server Template
if [ ! -z "$STATIC_SERVER" ]; then
 cp -vf /var/www/runtime/conf/nginx-static-server.conf /etc/nginx/conf.d/default.conf
elif [ ! -z "$LUA_SERVER" ]; then
 cp -vf /var/www/runtime/conf/nginx-lua-server.conf /etc/nginx/conf.d/default.conf
else
 cp -vf /var/www/runtime/conf/nginx-default-server.conf /etc/nginx/conf.d/default.conf
fi

# Set custom webroot
if [ ! -z "$WEBROOT" ]; then
 sed -i "s#root /var/www/app/public;#root ${WEBROOT};#g" /etc/nginx/conf.d/default.conf
fi

# Disable opcache
if [ ! -z "$OPcache" ]; then
 sed -i 's#zend_extension=opcache#;zend_extension=opcache#g' /usr/local/etc/php/php.ini
fi

# Increase the memory_limit
if [ ! -z "$PHP_MEM_LIMIT" ]; then
 sed -i "s/memory_limit = 256M/memory_limit = ${PHP_MEM_LIMIT}/g" /usr/local/etc/php/conf.d/php-custom.ini
fi

# Increase the post_max_size
if [ ! -z "$PHP_POST_MAX_SIZE" ]; then
 sed -i "s/post_max_size = 8G/post_max_size = ${PHP_POST_MAX_SIZE}/g" /usr/local/etc/php/conf.d/php-custom.ini
fi

# Increase the upload_max_filesize
if [ ! -z "$PHP_UPLOAD_MAX_FILESIZE" ]; then
 sed -i "s/upload_max_filesize = 8G/upload_max_filesize= ${PHP_UPLOAD_MAX_FILESIZE}/g" /usr/local/etc/php/conf.d/php-custom.ini
fi

# Start supervisord and services
exec /usr/bin/supervisord -n -c /etc/supervisord.conf
