buildout_proxy
==============

This pyramid app can be used as a cache proxy for buildout config files
stored remotly.

If a host is temporarily unavailable the cache file will be served.

Functionnalities :
 * Cache proxy for buildout files
 * Cache duration per domain
 * Login / password configuration
 * Limitation on allowed domains

Configuration
=============

buildout_proxy.directory
------------------------

The folder where the cached files will be stored, this should be an
absolute path

example : `buildout_proxy.directory = /tmp`

default : `/tmp`

buildout_proxy.allow.hosts
--------------------------

The list of allowed hosts

example :
```
buildout_proxy.allow.hosts =
    *github.com
    affinitic.be
```

default : `*`

buildout_proxy.hosts.passwords
------------------------------

The absolute path to a list of login/password for domains

example : `buildout_proxy.hosts.passwords = /tmp/.password`

file format example :
```
github.com = login:password
affinitic.be = login:password
```

buildout_proxy.allow.routes
---------------------------

The list of allowed routes

example :
```
buildout_proxy.allow.routes =
    resource
    merged
```

allowed values :
```
resource
merged
merged_section
```

default : `resource`

buildout_proxy.cache.default
----------------------------

The default cache duration for files (in seconds)

example : `buildout_proxy.cache.default = 86400`
default : `86400`

buildout_proxy.cache
--------------------

The cache duration per domain (in seconds)

example :
```
affinitic.be;ever
*github.com;never
google.com;3600
```

allowed values :
```
never
ever
integer
```
