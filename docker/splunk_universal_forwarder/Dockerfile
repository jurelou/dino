FROM splunk/universalforwarder:8.2.5

USER root

ADD --chown=splunk:splunk \
    config/inputs.conf \
    /opt/splunkforwarder/etc/system/local/inputs.conf

ADD --chown=splunk:splunk \
    config/outputs.conf \
    /opt/splunkforwarder/etc/system/local/outputs.conf

ADD --chown=splunk:splunk \
    config/props.conf \
    /opt/splunkforwarder/etc/system/local/props.conf

ADD --chown=splunk:splunk \
    config/transforms.conf \
    /opt/splunkforwarder/etc/system/local/transforms.conf

WORKDIR /opt/splunkforwarder
USER ansible
