import json
import signal
import logging
import requests
from os import path
from urllib.parse import urlunparse, urlencode, ParseResult
from configparser import ConfigParser
from logging.handlers import SysLogHandler


def set_logger(log_level):
    log_level = getattr(logging, log_level)
    logger = logging.getLogger('DynHost')
    base_format = '%(levelname)s - %(message)s'
    handler = SysLogHandler(address='/dev/log')
    formatter = logging.Formatter('%(name)s: ' + base_format)
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    logger.addHandler(handler)
    logger.setLevel(log_level)
    return logger


def get_config(config=None):
    if not config:
        config = ConfigParser(defaults={
                'dyndns_host': 'https://www.ovh.com',
                'dyndns_nic': '/nic/update',
                'loglevel': 'INFO',
                'cache_file': '/run/shm/DynHost.cache',
                'wildcard': 'OFF',
                'backmx': 'NO',
                'system': 'dyndns',
                'loop_time_sec': '60',
        })
    config.read([path.expanduser('~/.config/dynhost.cfg'), '/etc/dynhost.cfg'])
    set_logger(config.get(config.default_section, 'loglevel'))
    return config


def get_ip():
    logger = logging.getLogger('DynHost')
    try:
        ip = requests.get('http://www.monip.org')\
                .text.split('IP : ')[1].split('<br')[0]
    except Exception as error:
        logger.error("Couldn't retrieve IP: %r", error)
        return None
    logger.debug('read ip %r', ip)
    return ip


def push_dyn_ip(ip, section):
    logger = logging.getLogger('DynHost')
    logger.warning('sending %r to %r', ip, section.name)
    query = urlencode({'backmx': section.get('backmx'),
                       'hostname': section.get('domain'), 'myip': ip,
                       'system': section.get('system'),
                       'wildcard': section.get('wildcard')})

    url = ParseResult(section.get('dyndns_scheme'), section.get('dyndns_host'),
                      section.get('dyndns_path'), '', query, '')

    resp = requests.get(urlunparse(url),
            auth=(section.get('username'), section.get('password')))
    logger.warning('ipcheck ended with %r - %r', resp, resp.text)


def _get_cache_file_content(cache_file):
    try:
        with open(cache_file) as fd:
            return json.load(fd)
    except Exception:
        return {}


def read_cached_ip(cache_file, domain):
    return _get_cache_file_content(cache_file).get(domain)


def write_cache_ip(domain, ip, cache_file):
    caches = _get_cache_file_content(cache_file)
    caches[domain] = ip
    with open(cache_file, 'w') as fd:
        return json.dump(caches, fd)


def browse_config(config):
    logger = logging.getLogger('DynHost')

    current_ip = get_ip()
    if current_ip is None:
        return

    for section in config.values():
        if section.name == config.default_section:
            continue

        if not section.getboolean('enabled', fallback=True):
            logger.debug('section %r not enabled', section)
            continue

        cache_file = section.get('cache_file')
        domain = section.get('domain')

        past_ip = read_cached_ip(section.get('cache_file'), domain)

        if past_ip == current_ip:
            logger.debug("ip %r has not changed, doing nothing", current_ip)
            continue

        push_dyn_ip(current_ip, section)
        write_cache_ip(domain, current_ip, cache_file)



