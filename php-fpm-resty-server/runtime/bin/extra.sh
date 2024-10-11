#!/bin/bash

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