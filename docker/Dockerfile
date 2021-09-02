from ubuntu:20.04

# Environment Vars
ENV \
  WORKING_DIR=/spaasgm \
  BUILDPREFIX=docker \
  PYTHONUNBUFFERED=1

# Create workspace
RUN \
    mkdir ${WORKING_DIR} && cd ${WORKING_DIR}

# Install Utils
RUN \
    apt-get update && DEBIAN_FRONTEND="noninteractive" apt-get install gnupg curl wget apt-transport-https -y

# Install Java
RUN \
    apt-get install openjdk-8-jdk -y \
     && java -version

# install cassandra
RUN \
    echo "deb https://downloads.apache.org/cassandra/debian 40x main" | tee -a /etc/apt/sources.list.d/cassandra.sources.list \
    && curl https://downloads.apache.org/cassandra/KEYS | apt-key add - \
    && apt-get update \
    && DEBIAN_FRONTEND="noninteractive" apt-get install cassandra -y
#    && tail -f logs/system.log \
#    && sleep 10s \
#    && nodetool status

# Install Kafka
RUN \
    adduser kafka && adduser kafka sudo && su -l kafka \
    && mkdir ${WORKING_DIR}/kafka && cd ${WORKING_DIR}/kafka \
    && wget https://dlcdn.apache.org/kafka/2.8.0/kafka_2.13-2.8.0.tgz -O /tmp/kafka.tgz \
    && tar -xvzf /tmp/kafka.tgz --strip 1 \
    && rm /tmp/kafka.tgz

# Configure Kafka services
COPY ${BUILD_PREFIX}/docker/start-kafka.sh ${WORKING_DIR}/start-kafka.sh
RUN \
    chmod +x ${WORKING_DIR}/start-kafka.sh \
    && ${WORKING_DIR}/start-kafka.sh

# Install miniconda
RUN \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh \
    && chmod +x /tmp/miniconda.sh \
    && /tmp/miniconda.sh -b -p ${WORKING_DIR}/miniconda \
    && rm /tmp/miniconda.sh \
    && ln -s ${WORKING_DIR}/miniconda/etc/profile.d/conda.sh /etc/profile.d/conda.sh \
    && echo ". ${WORKING_DIR}/miniconda/etc/profile.d/conda.sh" >> ~/.bashrc \
    && echo "conda activate base" >> ~/.bashrc

# Make RUN commands use `bash --login`:
SHELL ["/bin/bash", "--login", "-c"]

## Initialize conda in bash config fiiles:
RUN conda update conda -y && \
    conda init bash && \
    conda clean --all

# Create the environment:
COPY ${BUILD_PREFIX}/comappenv.yaml ${WORKING_DIR}/comappenv.yaml
RUN conda env create -n comappenv -f ${WORKING_DIR}/comappenv.yaml && \
    conda activate comappenv && \
    conda clean --all

# Copy Files
COPY ./comapp ${WORKING_DIR}/comapp

# Copy and make entrypoint executable
COPY ./${BUILDPREFIX}/entrypoint.sh ${WORKING_DIR}/
RUN chmod +x ${WORKING_DIR}/entrypoint.sh

# Test
RUN timeout --preserve-status 3s bash -c ${WORKING_DIR}/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/spaasgm/entrypoint.sh"]
