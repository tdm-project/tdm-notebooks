FROM crs4/tdm-tools:latest
MAINTAINER simone.leo@crs4.it

RUN useradd -m jupyter && \
    pip install --no-cache-dir Cython && \
    pip install --no-cache-dir matplotlib jupyter xarray pyproj scipy && \
    pip install --no-cache-dir cartopy 

WORKDIR /home/jupyter
USER jupyter
RUN mkdir .jupyter
COPY --chown=jupyter jupyter_notebook_config.py .jupyter/
COPY --chown=jupyter check check_notebook.py ./
COPY --chown=jupyter notebooks notebooks

WORKDIR notebooks

EXPOSE 8888
ENTRYPOINT ["/bin/bash", "-c", "jupyter notebook"]
