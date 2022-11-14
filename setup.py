os_dict = {"Darwin": 0, "Windows": 1, "Linux": 2}
import os

def initialie_database(): 
    import docker
    """
        This initialize all the database that is required for hosting mqtt_web
    """
    client = docker.from_env()
    #Run credDB
    container = client.containers.run("mongo:latest", name="credDB", ports={'27017/tcp': '27017'}, detach=True)
    
if __name__ == "__main__":
    initialie_database(
