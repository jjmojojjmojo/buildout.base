========================================
buildout.base - the new, 'uber' buildout
========================================

References
==========
:zc.buildout: http://pypi.python.org/pypi/zc.buildout
:Apache Compilation Options: http://httpd.apache.org/docs/2.2/install.html
:Diazo Installation: http://diazo.org/deployment.html#apache
:mod_transform: https://launchpad.net/mod-transform
:zc.recipe.cmmi: http://pypi.python.org/pypi/zc.recipe.cmmi/
:zc.recipe.egg: http://pypi.python.org/pypi/zc.recipe.egg/
:mr.developer: http://pypi.python.org/pypi/mr.developer/
:cp.recipe.cmd: http://pypi.python.org/pypi/cp.recipe.cmd/

.. contents::

Assumptions
===========
This document and the basic buildout parts assume a Unix-like environment, specifically Debian or a derivitive (Ubuntu).

It assumes you understand the basic 'bootstrap-buildout-buildout' process, and are comfortable with the basic structure
of buildout's config files.

It also assumes that you are allowed to run commands as root via the ``sudo`` command.

Buildout Prerequisites
======================
In order to run *any* buildout, you must have the following installed:

 - Python (tested with Python 2.6/
 - the Python development packages
 - tools sufficient to compile source code (gcc, make)
 
The following command should install what you need:

::

    $ sudo apt-get install python python-dev build-essential


How Buildout Extension/Overriding Works
=======================================
Recall that ``zc.buildout`` will allow you to *extend* a config file. When that happens, the files are essentially merged. 

This is the core feature that is exploited in this buildout. It allows us to extend a very complex file, and then just tweak 
a setting or option here and there to suit our needs. The base file can evolve, be extended, enhanced, but the as long as its basic
structure stays the same, the derivitive files don't need to change.

One caveat: because the files are merged, and there is no concept of a namespace in zc.buildout config files, 
you have to ensure that any part name you use is unique across all of the config files.

Here's an example of the primary ways you can override the parts and values:

**base.cfg**

.. include:: examples/basics/base.cfg
   :literal:
   
    
If you extend a cfg file, any parts listed will be used ver batim from the base file, unless a part with the 
same name exists in the derivitive file. Then, any values specified will be used, overwrighting
the base file.

**extender.cfg**

.. include:: examples/basics/extender.cfg
   :literal:

The *effective* config file looks like this:

.. include:: examples/basics/buildout-dump.cfg
   :literal:
   
File Layout
===========
General config files that may/may not be in use are put into ./cfg. These include:

 - ``build.cfg`` - all compiled packages are set up here.
 - ``runit.cfg`` - process control with runit (blitzen.recipe.runit)
 - ``apache.cfg`` - configures apache (load balancing, proxying, SSL, etc)
 - ``plone.cfg`` - plone setup
 - ``django.cfg`` - set up a django project
 - ``settings.cfg`` - a centralized location for all settings that tend to change as a buildout is deployed in different places, referenced by the other files in the cfg directory, and overridden in the deployment files.
 - ``pre-install.cfg`` - defines common prerequisite steps to be taken before all others (uses cp.recipe.cmd) 
 - ``post-install.cfg`` - defines common steps to take after all others are complete (uses cp.recipe.cmd)

These are all very generic, and cover our typical production deployment use cases.
 
In the main directory are files that are expected to be very specific:

 - ``buildout.cfg`` - the default buildout file, expected to be production
 - ``development.cfg`` - a file tailored to a development environment
 - ``staging.cfg`` - configuration for the staging/testing server. This should be as close to the production settings as possible.
 - ``pre-install.cfg`` - deployment specific pre-buildout steps
 - ``post-install.cfg`` - deployment specific post-buildout steps

``development.cfg`` and ``staging.cfg`` should both extend the base ``buildout.cfg``.

``pre-install.cfg`` and ``post-install.cfg`` in the main directory differ from the ones in ``cfg`` in that
the steps defined in the cfg directory are required for use of the other parts (e.g. it installs
the build tools if they don't already exisist, or the runit package). In the main directory,
these files are intended to be 'deployment level' -- they do things like install a special pre-requesite 
package that's a dependancy for a specific plone product (say RelStorage).

Finally, there is a `bootstrap.py` file, which intitializes the buildout.

The initial configuration files are typical of our plone 4 deployments. Other deployment-local files
should also live in the root directory (for example, a local_settings.py file for a Django
app)
                 
There is also an examples directory, which contains common assemblies of the different
types of deployments we use:

 - ``plone`` - Plone 4 deployment stack (apache+plone+diazo+ssl) **TODO**
 - ``httpd`` - Just an Apache httpd deployment **TODO**
 - ``django`` - django+httpd **TODO**

Basic Usage
===========
TODO
----
 
Files And Components Explained
==============================
settings.cfg
------------
This file handles all of the common deployment-specific settings. It's used only as a reference, the parts defined don't have
recipes, and can not be executed.

Reference one of these settings in a config file like this (the variable substitution works
in any value, and many can be used at once):

   ::
       
       listen = ${listen:public}:${ports:public}
       user = ${users:plone}
   

The defaults are arbitrary but should work in any deployment.
       
Part: *listen*
##############
The IP addresses that the various services listen on. Typically, you can use 0.0.0.0 to mean "all IPs on this server".

:public: the internet address representing the 'public' or Internet interface.
:private: the internet address representing the 'private' or local LAN interface (e.g. 192.168.x.x)
:cluster: The load-balancer IP

Part: *names*
#############
DNS names used throughout the config files. Used mostly for url re-writing, to feed to the VHM in plone, etc.

:public: host name of the site (e.g. tpl.med.unc.edu or blitzen.unc.edu)

Part: *ports*
#############
The ports that the various services listen on.

With the exception of ``public`` and ``ssl``, you will typically never use a port number below 1024.

:plone[1-3]: the plone ZEO client ports. You typically won't use more than 3. 
:plone-direct[1-3]: 'punch through' ports used to communicate directly with the plone ZEO clients. These are used to bypass load balancing and for debugging/importing/etc.
:webdav: the WebDAV port. We typically set up one client as the 'webdav' client when using it with Plone.
:zeo: ZEO Server port.
:balancer: the port the load balancer listens on. Requests will typically be proxied from the public and/or ssl ports to the load balancer.
:public: the http port; in a production setting, this is almost always 80, but it's pulled out into a configurable variable for devleopment/staging.
:ssl: the ssl port; in a production setting, this is almost always 443, but sometimes you may need to do SSL over a different port in debugging/development.


Part: *users*
#############
Users and groups used to run the processes. We typically will set up separate user accounts for each service. This makes it easier to see which
stack is using what resources on multiple-site deployments.

:plone: The plone ZEO clients
:zeo: the ZEO server
:httpd: the apache HTTPd server
:group: a common group all users are put into. The idea is that permissions on the buildout directory will typically be 775, and all
        users that need read/write access will be in this group (that would typically include you as well).

Part: *ssl-settings*
####################
Options that often change for SSL configuration between development, staging, and production deployments.

:key_file: The key file used to generate the certificate 
:cert_file: the SSL certificate itself.

Part: *apache-settings*
#######################
Commonly changed settings for the httpd server.

:document_root: Where static files will be served from by default.  
:state_dir: location where various runtime files are kept (httpd's PID file, etc)
:pid_file: Process identifier file for httpd. Helps ``apachectl`` stop/restart the server.
:log_dir: Location of the log files.
:error_log: name of the error log file.
:access_log: name of the access log file.

.. note:: The erorr/access logs can be customized for individual virtual hosts, these are typically used for unified logging, or by default.

File Contents
#############
Here's the default ``settings.cfg`` file:

.. include:: cfg/settings.cfg
   :literal:


build.cfg
---------
This file uses (chiefly) ``zc.recipe.cmmi`` to download and compile various applications and python modules. Compiling things ourselves provides a few 
benefits over using precompiled binaries or system packages. These include: 

 - Compile-time optimization.
 - Access to new code/features not available to us otherwise.
 - Minimization of pre-buildout setup.
 - The buildout is more portable (the same buildout could *theorhetically* run on any platform where the right build tools were availalbe)
 - The buildout is self-contained (no dependancies on binaries/libraries outside of the buildout environment).

The basic usage of ``zc.recipe.cmmi`` is like this:

::
    
    [mypart]
    recipe = zc.recipe.cmmi
    url = url://to.source/package.tgz
    extra_options = 
        --options 
        --that 
        --are 
        --passed 
        --to 
        --configure
    
There are other options availalbe, but most packages will only use those three. 

In the event that the compilation fails, the source directory will be left in ``/tmp``. You can change to that directory and run:

::
    
    $ make
    
This should give you better output as far as what caused the compilation to fail. You can also use the ``-D`` option when running
the buildout to drop into a PDB interpeter session in the event of a failure.

You can overload parts of extra_options in extending ``.cfg`` files, here's a contrived example:

**build.cfg:**
::
    
   [mypart]
   recipe = zc.recipe.cmmi
   url = url://to.source/package.tgz
   extra_options = 
       --options 
       --that 
       --are 
       --passed 
       --to 
       --configure
       
**buildout.cfg:**

::
    
    [buildout]
    extends = build.cfg
    
    parts = mypart
    
    [mypart]
    extra_options += --debug-mode=superdooper
 
This will add the ``debug-mode`` option to the list passed to ``configure``.

.. note:: The build part **must** separate the extra_options onto separate lines for this to work.

File Contents
############# 
.. include:: cfg/build.cfg
   :literal:

Part: *libxml*
##############
Compiles the lxml2 library used by Plone, mod_transform, etc.

.. include:: cfg/build.cfg
   :literal:
   :start-line: 10
   :end-line: 13

We turn off building the python egg here since it doesn't work in this environment. It is handled by the ``lxml`` part.

Part: *libxslt*
###############
Compiles libxslt, used by mod_transform.

.. include:: cfg/build.cfg
   :literal:
   :start-line: 15
   :end-line: 19

Here we point to the ``libxml`` part since libxslt depends on it.


Part: *httpd*
#############
Compiles the Apache httpd server, version 2.2.x. Uses standard configuration options for our typical deployments. Installs in 
``parts/httpd`` (so the ``htttpd`` and ``apachectl`` executables will be in ``parts/httpd/bin``).

.. include:: cfg/build.cfg
   :literal:
   :start-line: 20
   :end-line: 31
   
Options summary:

==============================================     =====================================================================================================
Option                                             Explaination
==============================================     =====================================================================================================                                              
``--with-mpm=worker``                              uses the 'worker' multi-processing module. See http://httpd.apache.org/docs/2.2/mpm.html
``--enable-rewrite``                               adds in mod_rewrite, allows us to re-write urls
``--enable-proxy=shared``                          adds in mod_proxy, loadable (used for Plone cluster)
``--enable-proxy-balancer=shared``                 adds in mod_proxy_balancer, loadable (used for Plone cluster)
``--enable-logio``                                 compiles in mod_logio, we can add IO information to the logs for better resource consumption analysis.
``--enable-deflate``                               adds in gzip support for supported browsers (can increase responsiveness of pages at the cost of 
                                                   slight overhead)
``--enable-ssl=shared``                            makes the SSL module loadable at startup instead of compiled in.
``--enable-headers=shared``                        mod_headers, allows inspection of headers in rewrite rules
``--libexecdir=${buildout:directory}/modules``     set the module directory to a place outside of the httpd part; this prevents other modules (e.g., 
                                                   mod_transform) from being whacked when apache is recompiled.
``--sysconfdir=${buildout:directory}/conf``        put the conf directory in a location that can be easily accessed by the user.
``--bindir=${buildout:directory}/bin``             put all of the binaries into the buildout's ``bin`` directory.
``--sbindir=${buildout:directory}/bin``            ... and all of the other binaries (``apachectl``, ``htpasswd``)
``--with-expat=${expat:location}``                 we're using our own expat due to problems with the built-in one and the one in python.
==============================================     =====================================================================================================


Part: *mod_transform*
#####################
We use mod_transform for theming. We have to compile a special version with HTML support.

.. include:: cfg/build.cfg
   :literal:
   :start-line: 33
   :end-line: 39
   
The options point at the ``axps`` binary, which the module uses to figure out where the httpd header files and module installation directory live.

Part: *mod_wsgi*
################
Compiles the WSGI support for Apache. See: http://code.google.com/p/modwsgi/.

Part: *expat*
#############
Custom-compiles the expat XML library for apache, due to some weirdness with the expat that comes with apache, the system one that comes with debian,
and the one built into python. See: http://expat.sourceforge.net/.

Part: *libjpeg*
###############
Compiles the libjpeg library, used by PIL. We're opting to use the libjpeg-turbo variant. It's supposed to be much faster
than the standard libjpeg lib.

.. include:: cfg/build.cfg
   :literal:
   :start-line: 41
   :end-line: 43
   
Part: *freetype*
################
Sets up the freetype library, used by PIL.

.. include:: cfg/build.cfg
   :literal:
   :start-line: 45
   :end-line: 47
   
Parts: *lxml-env* and *lxml*
############################
Compiles the pyton lxml2 module. The ``lxml-env`` part is used to define the environment variables set during compilation.

.. include:: cfg/build.cfg
   :literal:
   :start-line: 49
   :end-line: 65
   
This part uses ``zc.recipe.egg``. The python lxml2 module is not easily installed in a buildout environment. The parameters passed
to ``zc.recipe.egg``, along with the environment defined in ``lxml-env`` make it happy so it will compile and install.

Part: *pil*
###########
Installs and compiles PIL, the python imaging library. Used by Plone. Here we're using a specially bundled package that doesn't
require TK, called ``Pillow``.

.. include:: cfg/build.cfg
   :literal:
   :start-line: 67
   
   
Examples
========
httpd
-----
This example sets up an apache httpd server instance set to run on port 8008.

File Layout
###########
The main configuration files, specifically ``httpd.conf`` are placed in the root of the buildout.

The ``www`` directory is set as the document root. There is an ``index.html`` file included to give you something to look at.
An entire static website could be put in this directory.

The ``httpd.conf`` file is generated via the ``z3c.recipe.template`` recipe. The template for ``httpd.conf`` is located in the
``templates`` directory. The template file uses the ``zc.buildout`` variable-substitution syntax, and has access to all of the
values defined in the buildout.

Logs are stored in ``var``.

Usage
#####

::
    
    $ cd examples/httpd
    $ python bootstrap.py
    $ bin/buildout
    ... time passes ...
    $ bin/apachectl start
    
Now if you open your browser to http://ipaddress-of-machine:8008, you will see the index page.

To look at the logs:

::
    
    $ tail -f var/error.log var/access.log

To stop:

::
    
    $ bin/apachectl stop
    
Here's what the configuration file looks like:

.. include:: examples/httpd/templates/httpd.conf.in
   :literal:

The first line is telling apache to keep it's state file in the ``var`` directory. This prevents it from being deleted when/if apache gets recompiled while its running.

The rest of the file is essentially the bare-minimum you need to serve static files with apache. We've set the ``DocumentRoot`` to the ``www`` directory in the 
buildout, where we've placed an ``index.html`` file so you'll have something to look at.

One special section, however, exists for the sake of extensibility. The ``Include`` statement tells apache to pull in all the files within a certain directory to use
as additional configuration.

Update Proceedure
#################
If you need to change the configuration, it's possible to edit the generated ``httpd.conf`` directly, but that should only be done in emergency situations.

This is the typical proceedure (assuming you've edited ``conf/httpd.conf.in``):

::
    
    $ bin/buildout -oN install httpd-conf
    $ bin/apachectl graceful
    
The first command runs the buildout, but prevents buildout from going online, and looking for newer python eggs. The ``install httpd`` clause is telling buildout to only install the ``httpd-conf`` part
if it has changed.

The second command tells apache to reload its configuration data. This will not disconnect users mid-request.

Adding SSL
##########
SSL support requires a few more configuration parts. Specifically:

 - We need an SSL certificate and key file
 - We need to add additional configuration information to apache to make it load mod_ssl
 - We need to set up a virtual host listening on the SSL port
 
Here's what ``ssl.cfg`` looks like:

.. include:: examples/httpd/ssl.cfg
   :literal:

   
We can see that we've over-written the ``ssl`` port from ``settings.cfg``, added a part that will generate a self-signed certificate for us from ``cfg/post-install.cfg``,
and dropped a new template into the ``conf.d`` directory mentioned in ``httpd.conf``. 

We've also specified the location of our SSL certificate and key file. In production, these would not point to a self-signed certificate, but instead to one that we purchased.

The ``ssl.conf.in`` file looks like this:

.. include:: examples/httpd/templates/ssl.conf.in
   :literal:

This, again, is the bare-minimum configuration necessary to do SSL with apache.

To enable ssl, use the ``-c`` command line option to ``bin/buildout``, specifying ``ssl.cfg``:

::
    
    $ bin/buildout -c ssl.cfg
    
Then restart apache:

::
    
    $ bin/apachectl graceful
    
Now going to https://ipaddress-of-machine:8009 will bring up our ``index.html`` file, after we tell our browser that we're OK with a possibly suspect SSL certificate.

Moving To Production
####################
In a production situation, you may have static files in the document root, and will likely have more complicated configuration templates.

The only thing that really has to change are the ``ssl-settings`` parameters, and the names/ports in ``settings.cfg``. You will typically want to set a user and group 
in ``httpd.conf.in``, and run apachectl as root.
   
plone
-----
Major Components
################
A plone site is really a stack of a handful of applications, running in tandem.

django
------
TODO
####


