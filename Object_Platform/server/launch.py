from server import app

version = '0.1.0'
host_ip = "0.0.0.0"
host_port = "80"

if __name__ == '__main__' :
    
    print('------------------------------------------------')
    print('Cloud9 CV - version ' + version )
    print('------------------------------------------------')
    
    app.run( host=host_ip, port=host_port)
