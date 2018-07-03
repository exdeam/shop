#!/bin/sh

# Make sure spool directory is writable (if a mounted volume)
chown Debian-exim /var/spool/exim4
chown Debian-exim /exim-saved
chown Debian-exim /var/log/exim4

cp -r /etc/exim-orig/* /etc/exim4/
echo ${PRIMARY_HOST} >/tmp/primary_host
echo ${ALLOWED_HOSTS} >/tmp/allowed_hosts
echo ${DKIM_SELECTOR} >/tmp/dkim_selector

/usr/sbin/exim4 ${*:--bdf -q30m} &
EXIM_PID=$!
clean_up() {
    echo 'Killing Exim...'
    kill $EXIM_PID
}
trap clean_up SIGINT SIGTERM
wait $EXIM_PID
