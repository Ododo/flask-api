from docker import get_docker_ip


def make_config_file(uuid, d_id):
	f = open("/etc/nginx/docker/"+uuid+".conf", w)
	f.write("location /" + uuid + " {")
	f.write("	proxy_pass " + get_docker_ip(d_id))
	f.write("}")
	f.close();

def del_config_file(uuid):
	call("rm -f /etc/nginx/docker/"+uuid+".conf");

def reload_nginx():
	call("/etc/init.d/nginx restart");
