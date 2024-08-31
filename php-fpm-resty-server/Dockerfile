#Custom Server on top of php-fpm & openrusty nginx

FROM jonayedhossan/php-fpm-resty:latest

LABEL maintainer="Jonayed Hossan Gazi <me@zuna.id>"

#use custom config file
ADD app/app-conf/ /var/www/app-conf/
ADD app/app-cli-scripts /var/www/app-cli-scripts/
ADD app/app-conf/supervisord.conf /etc/supervisord.conf
ADD app/app-conf/php-fpm.conf /usr/local/etc/php-fpm.conf
ADD app/app-conf/php-fpm-pool.conf /usr/local/etc/php-fpm.d/www.conf
ADD app/app-conf/php-custom-ini.conf /usr/local/etc/php/conf.d/php-custom.ini
#ADD app/conf/nginx.conf /etc/nginx/nginx.conf
#ADD app/conf/nginx-server.conf /etc/nginx/default.conf
ADD app/app-conf/nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
ADD app/app-conf/nginx-server.conf /etc/nginx/conf.d/default.conf

# copy all code
ADD app/ /var/www/app/

EXPOSE 80

WORKDIR "/var/www/app/public"

CMD ["bash", "/var/www/app-cli-scripts/start.sh"]

STOPSIGNAL SIGQUIT
