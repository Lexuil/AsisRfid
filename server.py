
from microWebSrv import MicroWebSrv

srv = MicroWebSrv(webPath='www/')

def servinit():
	srv.Start()

def servdeinit():
	srv.Stop()


