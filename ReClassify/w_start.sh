docker run -d -p 9881:1883 -v ${PWD}/mosquitto:/mosquitto/config/ eclipse-mosquitto:latest
cd OBJweb
docker image build . -t ekstrah/objweb:latest
docker run -d -p 8080:8080 -p 9999:9999/udp ekstrah/objweb:latest 8080 9999 9881 test