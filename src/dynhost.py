#!/usr/bin/python3.4
import json
import logging
import requests
from os import path
from urllib.parse import urlunparse, urlencode, ParseResult
from configparser import ConfigParser
from logging.handlers import SysLogHandler
from functools import lru_cache


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


def get_config():
    config = ConfigParser(defaults={
            'dyndns_host': 'https://www.ovh.com',
            'dyndns_nic': '/nic/update',
            'loglevel': 'INFO',
            'cache_file': '/run/shm/DynHost.cache',
            'wildcard': 'OFF',
            'backmx': 'NO',
            'system': 'dyndns',
    })
    config.read([path.expanduser('~/.config/dynhost.cfg'), '/etc/dynhost.cfg'])
    set_logger(config.get(config.default_section, 'loglevel'))
    return config


logger = logging.getLogger('DynHost')


@lru_cache(maxsize=None)
def get_ip():
    ip = requests.get('http://www.monip.org')\
            .text.split('IP : ')[1].split('<br')[0]
    logger.debug('read ip %r', ip)
    return ip


def push_dyn_ip(ip, section):
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


def main():
    config = get_config()
    for section in config.values():
        if section.name == config.default_section:
            continue

        if not section.getboolean('enabled', fallback=True):
            logger.debug('section %r not enabled', section)
            continue

        cache_file = section.get('cache_file')
        domain = section.get('domain')

        past_ip = read_cached_ip(section.get('cache_file'), domain)

        if past_ip == get_ip():
            logger.debug("ip %r has not changed, doing nothing", get_ip())
            continue

        push_dyn_ip(get_ip(), section)
        write_cache_ip(domain, get_ip(), cache_file)


if __name__ == '__main__':
    main()
