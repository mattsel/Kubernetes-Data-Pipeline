FROM continuumio/miniconda3:latest

WORKDIR /app

COPY environment.yml .
COPY . .

RUN conda env create -f environment.yml

ENV PATH /opt/conda/envs/myenv/bin:$PATH

CMD ["bash", "-c", "source activate kube-logs && python filebeat_config_generator.py"]
