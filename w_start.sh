# docker run -p 9881:1883 -v ${PWD}/mosquitto:/mosquitto/config/ eclipse-mosquitto:latest
cd OBJweb
docker image build . -t ekstrah/objweb:latest