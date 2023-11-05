# Pull base image
FROM python:3.10.2-slim
# Set environment varibles
ENV API_KEY "api_key"
ENV API_SECRET "api_secret"

COPY ./TA-lib/ /
RUN pip install ta-lib

#se descarga el paquete de TA-lib
#RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \

#comandos para compilar, instalar y ejecutar el paquete de TA-lib
#RUN apt update \
#    && apt install -y gcc build-essential \
#    && tar -xzf ta-lib-0.4.0-src.tar.gz \
#    && rm ta-lib-0.4.0-src.tar.gz \
#    && cd ta-lib/ \
#    && ./configure --prefix=/usr \
#    && make \
#    && make install \
#    && cd ~ \
#    && rm -rf ta-lib/ \
#    && pip install ta-lib

WORKDIR /code/
# Install dependencies
#RUN pip install pipenv
#COPY Pipfile Pipfile.lock /code/
#RUN pipenv install --system --dev
#pip3 install TA-Lib
#conda install -c conda-forge ta-lib
RUN pip3 install numpy \
    && pip3 install pandas \
    && pip3 install matplotlib \
    && pip3 install python-binance 
COPY ./code/ /code/
EXPOSE 8000
CMD ["python", "bot3.py"]