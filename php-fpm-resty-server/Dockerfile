FROM jonayedhossan/php-fpm-resty:latest

LABEL maintainer="Jonayed Hossan Gazi <me@zuna.id>"

RUN mkdir -m 0777 -p /var/www/app/public

WORKDIR "/var/www/app/public"

ADD app/ /var/www/app/
ADD runtime/ /var/www/runtime/

ADD runtime/conf/supervisord.conf /etc/supervisord.conf
ADD runtime/conf/php-fpm.conf /usr/local/etc/php-fpm.conf
ADD runtime/conf/php-fpm-pool.conf /usr/local/etc/php-fpm.d/www.conf
ADD runtime/conf/php-custom-ini.conf /usr/local/etc/php/conf.d/php-custom.ini

ADD runtime/conf/nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
ADD runtime/conf/nginx-default-server.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["bash", "/var/www/runtime/bin/init.sh"]

STOPSIGNAL SIGQUIT
