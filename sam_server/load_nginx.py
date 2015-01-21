#! /env/bin/python3
"""
load_nginx
Reloads nginx with the config specified in the nginx config
file (sam_server/nginx.conf).

Any references to environment variables in the config file are replaced
and the result is written to /etc/nginx/sites-enabled.

nginx is then restarted to load the config.


NOTE:
Running the script requires sudo permissions
"""
import os
import re
import sys
import subprocess
import tempfile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sam_server.settings')
from django.conf import settings

from pystache.parser import parse as parse_template
from pystache.renderer import Renderer

NGINX_CONFIG = 'sam_server/nginx.conf'
DELIMITERS = ('${', '}')

## If nginx installed using brew on OSX, this won't exist.
## Create the directory and edit '/usr/local/etc/nginx/sites-enabled/nginx.conf'
## In the http block, add this line:
##      include /etc/nginx/sites-enabled
SITES_ENABLED_DIR = '/etc/nginx/sites-enabled'

SIMPLE_SETTING = re.compile('^[A-Z_]+$')

DJANGO_SETTINGS = {
    k: getattr(settings, k)
    for k in dir(settings) if SIMPLE_SETTING.match(k)
}


def _check_envvar_exists(envvar):
    """
    Check that the specified variable is defined either in the environment
    of the user or in the django settings module
    """
    if envvar not in DJANGO_SETTINGS:
        print('{0} was not defined in django settings module'.format(envvar))
        sys.exit(1)


def compile_config_file(outfile):
    """
    Compile the config file, replacing all templated variables with their values

    outfile is a file-like object to write the compiled template into
    """
    print('Compiling {0}'.format(NGINX_CONFIG))
    with open(NGINX_CONFIG) as config_file:
        template = parse_template(
            config_file.read(),
            delimiters=DELIMITERS
        )
    ## Check that all the environment variables
    ## defined in the config file exist
    for node in template._parse_tree:
        if not isinstance(node, str):
            key = node.key
            _check_envvar_exists(key)
    renderer = Renderer()
    context = dict(os.environ)
    context.update(DJANGO_SETTINGS)
    output = renderer.render(template, context)
    with open(outfile, 'w+b') as f:
        f.write(bytes(output, encoding='utf-8'))


def enable_site(config_file):
    """
    Copy the config file to the sites-enabled directory
    """
    # check that nginx serves from /etc/nginx/sites-enabled
    if not os.path.exists(SITES_ENABLED_DIR):
        print('If installed using brew on OSX, the sites-enabled directory does \n'
              'not exist. Create it and add the following line to \n'
              '/usr/local/etc/nginx/nginx.conf inside the http \n'
              'block:\n'
              '\tinclude /etc/nginx/sites-enabled/*;\n')
        sys.exit(1)

    out_path = os.path.join(SITES_ENABLED_DIR, 'sam_server_nginx.conf')
    print('Writing config to {0}'.format(out_path))
    #print(config_file.read())
    print('Requires root permissions')
    ## cp is a bash command, so requires shell=True
    return_code = subprocess.call(['/usr/bin/sudo', 'cp', config_file, out_path])
    if return_code != 0:
        sys.exit(return_code)
    return_code = subprocess.call(['/usr/bin/sudo', 'chmod', '664', out_path])
    print('Copy completed successfully')


def restart_nginx():
    if sys.platform == 'darwin':
        subprocess.call(['nginx', '-s', 'reload'])
    elif sys.platform == 'linux':
        print('Restarting nginx (requires root permissions)')
        subprocess.call(['/usr/bin/sudo', '/etc/init.d/nginx', 'restart'])
    else:
        print('Could not restart nginx on {0}'.format(os.name))


if __name__ == '__main__':
    _check_envvar_exists('PROJECT_ROOT')
    proj_root = DJANGO_SETTINGS['PROJECT_ROOT']

    print('chdir {0}'.format(proj_root))
    os.chdir(proj_root)
    config_file = tempfile.NamedTemporaryFile(delete=False)
    compile_config_file(config_file.name)
    enable_site(config_file.name)
    os.remove(config_file.name)
    #outfile.close()
    restart_nginx()









