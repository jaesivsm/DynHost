# DynHost
Multiple DynDNS updating script

## Purpose

This script supports the [OVH](https://www.ovh.com) API for dynamic DNS updates. It allows you to specify several host to update with your public IPv4.

OVH originally distributed a script from which I'm freely inspired.

## Installation

You can install the script manually or simply use the [pypi](https://pypi.org/project/DynHost/) package through ``pip``.

```bash
pip3 install DynHost
```

### Edit the configuration

DynHost entire behavior is dictated by a configuration file which can be located either at ``~/.config/dynhost.cfg`` or at ``/etc/dynhost.cfg``. They have to be written in the [INI](https://en.wikipedia.org/wiki/INI_file).

Here's a short configuration example:

```cfg
[myDomain]
username=jaesivsm
password=MyPassword
domain=mydomain.com
 ```

What you have to know about that file is that every " section " is an FQDN that you can update. The title of the section is of no importance but it's advised to put something recognisable. Three option are mandatory for each section :
 * ``username``: The username given by your DNS provider for its API.
 * ``password``: The password you've chosen for that entry.
 * ``domain``: The domain to update.

A special section named ``DEFAULT`` can be added, it will hold default values for all the other sections.
Here are the different option available in the default section:
 * ``dyndns_host``, ``dyndns_nic``, ``back_mx``, ``system``, ``wildcard``: Those are option directly passed to the remote dynhost system. You won't have to update them if you're using OVH.
 * ``loglevel``: The verbosity of the script, available levels are, from the least to the most verbose : DEBUG, INFO, WARNING, ERROR and FATAL.
 * ``cache_file``: The path to the file the script will write the cache file. The default path aim at a ``/run/`` subfolder, which is supposed to be in-memory but you can put it wherever you waant.
 * ``loop_time_sec``: only if ran through SystemD, the wait time between to run in seconds, see the SystemD chapter about that.

*Note: you can also copy it in your private home folder in ```~/.config/``` but you'll have to run the script as your own user (so no SystemD)*

#### If you want to use SystemD

Find and activate the SystemD service file. Be aware that its path may vary depending on you systemd configuration: for example, as root on a debian Stretch, the service was copied here ``/usr/local/lib/python3.5/dist-packages/etc/systemd/system/dynhost.service`` by pip.

You can also copy it from the repository.

```bash
systemctl enable <path to dynhost.service>
systemctl daemon-reload
systemctl start dynhost.service
```

You should see SystemD tell you the service is ok and running with :
```bash
systemctl status dynhost.service
```

#### If you want to use cron
Edit the crontab you want and set it to run every few minutes.

```
*/2 * * * * /usr/local/bin/dynhost
```

# Debugging

All Dynhost logs are forwarded to SysLog so ``grep DynHost /var/log/syslog`` should be enough. You can also use SystemD logging mechanism if you're using it.
