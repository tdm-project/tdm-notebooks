FROM crs4/tdm-tools:latest
MAINTAINER simone.leo@crs4.it

RUN useradd -m jupyter && \
    pip install --no-cache-dir matplotlib jupyter

WORKDIR /home/jupyter
USER jupyter
RUN mkdir .jupyter notebooks
COPY jupyter_notebook_config.py .jupyter/
COPY radar notebooks/radar
WORKDIR notebooks

EXPOSE 8888
ENTRYPOINT ["/bin/bash", "-c", "jupyter notebook"]
