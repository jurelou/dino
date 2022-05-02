FROM splunk/splunk:8.2.6

USER root
WORKDIR /opt/splunk

COPY --chown=splunk:splunk \
    config/default.yml \
    /tmp/defaults/default.yml

ADD --chown=splunk:splunk \
    config/indexes.conf \
    etc/system/local/indexes.conf

COPY --chown=splunk:splunk \
    config/user-seed.conf \
    etc/system/local/user-seed.conf

ADD --chown=splunk:splunk \
    config/inputs.conf \
    etc/system/local/inputs.conf

ADD --chown=splunk:splunk \
    config/server.conf \
    etc/system/local/server.conf

ADD --chown=splunk:splunk \
    config/props.conf \
    etc/system/local/props.conf

# ADD --chown=splunk:splunk \
#     config/transforms.conf \
#     /opt/splunkforwarder/etc/system/local/transforms.conf

USER ansible