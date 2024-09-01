docker run -it --rm -p 8080:80 jonayedhossan/php-fpm-resty-server:latest
#docker run -d --restart=always -p 8080:80 -v /root/wapka_fm:/var/www/app/src:rw jonayedhossan/php-fpm-resty-server:latest
#docker run -d --restart=always -p 2122:80 -d  -e 'STATIC_SERVER=yes' -v /root/filemanager:/var/www/app/public:ro jonayedhossan/php-fpm-resty-server:latest
