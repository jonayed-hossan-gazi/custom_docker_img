FROM php:8.3.12-fpm-bullseye

LABEL maintainer="Zunaid Hossan Gazi <me@zuna.id>"

RUN apt-get update -y && apt-get upgrade -y  && \
  apt-get install -y curl wget tar zip libicu-dev libxslt-dev libsqlite3-dev libzip-dev liblua5.1-dev libonig-dev \
  libjudy-dev nghttp2 libbz2-dev libcurl4-openssl-dev libffi-dev libgmp-dev libuv1-dev libfreetype-dev libfreetype6 \
  libjpeg62-turbo libpng-tools libpng16-16 libfreetype6-dev libjpeg62-turbo-dev libpng-dev libbrotli-dev \
  supervisor ncdu ranger nano tree htop rsync libc-client-dev libkrb5-dev

RUN wget https://getcomposer.org/installer -O /tmp/composer-setup.php && \
  php /tmp/composer-setup.php --quiet --install-dir=/usr/bin --filename=composer && \
  rm /tmp/composer-setup.php

RUN docker-php-ext-configure gd --with-freetype --with-jpeg && \
  docker-php-ext-configure imap --with-kerberos --with-imap-ssl && \
  docker-php-ext-install gd imap pdo_mysql mysqli pdo_sqlite exif intl pcntl \
  xsl soap zip mbstring sockets bcmath calendar ctype filter ftp gmp ffi && \
  pecl install -o -f redis && \ 
  pecl install -o -f luasandbox && \
  pecl install apcu && \
  docker-php-ext-enable luasandbox redis gd apcu imap && \
  docker-php-source delete && rm -rf /tmp/* /var/lib/apt/lists/* && apt-get clean

ADD php-fpm.conf /usr/local/etc/php-fpm.conf
ADD php-fpm-pool.conf /usr/local/etc/php-fpm.d/www.conf
ADD php-custom-ini.conf /usr/local/etc/php/conf.d/php-custom.ini

RUN cp -v "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini" && \
  sed -i \
  -e "s/;opcache/opcache/g" \
  -e "s/;zend_extension=opcache/zend_extension=opcache/g" \
  "$PHP_INI_DIR/php.ini"

EXPOSE 9000

CMD ["php-fpm"]

STOPSIGNAL SIGQUIT

#orginal docker file link
#https://github.com/docker-library/php/blob/9c81d9730c629b700b88ef22c87839a9d6ab046b/8.3/bullseye/fpm/Dockerfile

