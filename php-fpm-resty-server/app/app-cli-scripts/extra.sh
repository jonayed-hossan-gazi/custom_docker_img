#!/bin/bash


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
 sed -i "s/post_max_size = 4G/post_max_size = ${PHP_POST_MAX_SIZE}/g" /usr/local/etc/php/conf.d/php-custom.ini
fi

# Increase the upload_max_filesize
if [ ! -z "$PHP_UPLOAD_MAX_FILESIZE" ]; then
 sed -i "s/upload_max_filesize = 4G/upload_max_filesize= ${PHP_UPLOAD_MAX_FILESIZE}/g" /usr/local/etc/php/conf.d/php-custom.ini
fi

if [ ! -z "$PUID" ]; then
  if [ -z "$PGID" ]; then
    PGID=${PUID}
  fi
  deluser nginx
  addgroup -g ${PGID} nginx
  adduser -D -S -h /var/cache/nginx -s /sbin/nologin -G nginx -u ${PUID} nginx
  echo "Created New User"
else
  if [ -z "$SKIP_CHOWN" ]; then
    chown -Rf nginx.nginx /var/www/app
  fi
fi

# Run custom scripts
if [[ "$RUN_SCRIPTS" == "1" ]] ; then
  scripts_dir="${SCRIPTS_DIR:-/var/www/app/scripts}"
  if [ -d "$scripts_dir" ]; then
    if [ -z "$SKIP_CHMOD" ]; then
      # make scripts executable incase they aren't
      chmod -Rf 750 $scripts_dir; sync;
    fi
    # run scripts in number order
    for i in `ls $scripts_dir`; do $scripts_dir/$i ; done
  else
    echo "Can't find script directory"
  fi
fi

if [ -z "$SKIP_COMPOSER" ]; then
    # Try auto install for composer
    if [ -f "/var/www/app/composer.lock" ]; then
        if [ "$APPLICATION_ENV" == "development" ]; then
            #composer global require hirak/prestissimo
            composer install --working-dir=/var/www/app
            composer install --working-dir=/var/www/app/public
            composer install --working-dir=/var/www/app/src
        else
            #composer global require hirak/prestissimo
            composer install --no-dev --working-dir=/var/www/app
            composer install --no-dev --working-dir=/var/www/app/public
            composer install --no-dev --working-dir=/var/www/app/src
        fi
    fi
fi