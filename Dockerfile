FROM arm64v8/debian:bookworm

# Install sudo, dos2unix, and create test user in a single layer
RUN apt update && \
    apt install -y --no-install-recommends sudo dos2unix && \
    groupadd -r test && \
    useradd -r -g test test && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Configure sudo for the 'test' user to run commands without a password
RUN echo "test ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    chmod 0440 /etc/sudoers # Restrict permissions on sudoers file

WORKDIR /scripts

# Copy scripts
COPY setup.sh /scripts/
COPY scripts /scripts/scripts

# Make scripts executable and convert line endings
RUN chmod +x /scripts/setup.sh && \
    chmod +x /scripts/scripts/* && \
    dos2unix /scripts/setup.sh && \
    dos2unix /scripts/scripts/*

# Set ownership to test user (optional but recommended)
RUN chown -R test:test /scripts

USER test

CMD ["/scripts/setup.sh"]