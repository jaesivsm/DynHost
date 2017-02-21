# DynHost
Multiple DynDNS updating script

## Purpose

This script is aimed at replacing the DynHost script which I was provided by my DNS provider and that I found unable to update multiple DNS records at once.

This script is basically a copy of the later one, rewritten and updated.

## Installation

You have two choices here:
 * You can use the dynhost.service file to make this a systemd service
 * You can use this script as a independent script
Both procedure will be explained below but start the same way.

#### Dependancies

You'll have to install ``python3-requests`` on your system one way or another (through the system package manager (apt, yum, pacman, rpm, ...) or through a python package manager like pip).

### Copy and install from the source

Note that you can install it either directly on your system (which will require admin privileges) or in an virtualenv (which will prevent you from using DynHost through SystemD).

```bash
git clone https://github.com/jaesivsm/DynHost.git
cd DynHost
python3 setup.py install
```

### Copy and edit the configuration

```bash
cp dynhost-sample.cfg /etc/dynhost.cfg
```

You'll then have to update your configuration file. Here are the different option available in the default section :
 * ``dyndns_host``, ``dyndns_nic``, ``back_mx``, ``system``, ``wildcard``: Those are option directly passed to the remote dynhost system. You won't have to update them if you're using OVH.
 * ``loglevel``: The verbosity of the script, available levels are, from the least to the most verbose : DEBUG, INFO, WARNING, ERROR and FATAL.
 * ``cache_file``: The path to the file the script will write the cache file. The default path aim at a ``/run/`` subfolder, which is supposed to be in-memory but you can put it wherever you waant.
 * ``loop_time_sec``: only if ran through SystemD, the wait time between to run in seconds

Each section you'll put after that will be considered a host to update. The title of the section is of no importance but it's advised to put something recognisable. Three option are mandatory for each section :
 * ``username``: The username given by your DNS provider for its API.
 * ``password``: The password you've chosen for that entry.
 * ``domain``: The domain to update.

Here's an example:

```cfg
[myDomain]
username=jaesivsm
password=MyPassword
domain=mydomain.com
 ```

*Note: you can also copy it in your private home folder in ```~/.config/``` but you'll have to run the script as your own user (so no SystemD)*

#### If you want to use SystemD

Link the service file (path may vary depending on you systemd configuration) and launch the service.

```bash
systemctl daemon-reload
service dynhost start
```

You should see SystemD tell you the service is ok and running with :
```bash
service dynhost status
```

#### If you want to use cron
Edit the crontab you want and set it to run every few minutes and don't forget the --once option.

```
*/2 * * * * /usr/local/bin/dynhost
```

# Debugging

All Dynhost logs are forwarded to SysLog so ``grep DynHost /var/log/syslog`` should be enough. You can also use SystemD logging mechanism if you're using it.
