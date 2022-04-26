FROM splunk/splunk:8.2.6

USER root

COPY --chown=splunk:splunk \
    config/default.yml \
    /tmp/defaults/default.yml

ADD --chown=splunk:splunk \
    config/indexes.conf \
    /opt/splunk/etc/system/local/indexes.conf

COPY --chown=splunk:splunk \
    config/user-seed.conf \
    /opt/splunk/etc/system/local/user-seed.conf

ADD --chown=splunk:splunk \
    config/inputs.conf \
    /opt/splunk/etc/system/local/inputs.conf

# ADD --chown=splunk:splunk \
#     config/outputs.conf \
#     /opt/splunkforwarder/etc/system/local/outputs.conf

ADD --chown=splunk:splunk \
    config/props.conf \
    /opt/splunk/etc/system/local/props.conf

# ADD --chown=splunk:splunk \
#     config/transforms.conf \
#     /opt/splunkforwarder/etc/system/local/transforms.conf

WORKDIR /opt/splunk
USER ansible