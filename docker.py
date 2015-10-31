from subprocess import call, check_output, STDOUT

def create_docker(name):
	return check_output(["docker", "run", "-d", name], stderr=STDOUT)

def get_docker_ip(d_id):
	return check_output(["docker", "inspect", "-f", "\"{{ .NetworkSettings.IPAddress }}\"", d_id], stderr=STDOUT)

def stop_docker(name):
	call(["docker", "stop", name])
	call(["docker", "rm", name])
