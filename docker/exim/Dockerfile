FROM bitnami/minideb:jessie

RUN install_packages exim4 \
 && rm -rf /etc/exim4/*

ADD start.sh /entrypoint.sh

VOLUME /etc/exim-orig
VOLUME /var/spool/exim4
VOLUME /var/log/exim4

EXPOSE 25

STOPSIGNAL SIGINT
ENTRYPOINT ["/entrypoint.sh"]