

ToolBox
=======

:Status: Work in progress

.. contents:: Table of Contents
    :depth: 2

Goal
----

A platform to share gadgets which helps the development.

Developer could release their own gadgets on pypi.  The gadgets will
be auto-plugged into the TurboGears 2 toolbox through setuptools.

ToolBox itself is a TurboGears 2 Application. Developers could use the
same skills to develop a toolbox gadget as they do to createa a
TurboGears 2 application.


Terminology
-----------

 * Gadget: The application working within toolbox. Some of them may
   allow you to embed them into your application.

Features
--------

 - Provide 'paster toolbox' command to start.
 - Provide a Gadget skeleton generator by paste script (not implement
   yet)
 - You could release your own gadgets on pypi.
 - Could detect if toolbox runs inside a project.
 - Able to select icons from Tango Icon
   http://tango.freedesktop.org/Tango_Icon_Library

Basic Gadgets
-------------

ToolBox 2 Basic Gadgets are a minimum set of gadgets to provide some
basic functions.

 - TGInfo gadget: browse tg2 related packages, similar to 'paster
   tginfo' command
 - TurboGears 2 API gadget: browse tg2 API
 - ToolBox 2 API gadget: browse ToolBox2 API
 - Design gadget (Project Browser), update from ToolBox template browser gadget.
 - Admin gadget (the successor to catwalk) from dbsprockets module

Spec
----

 - Setuptool-based plugin system

You could define gadget hooker in setup.py:

.. code-block:: ini

  [turbogears2.toolboxcommand]

 - To specify the Gadget should be worked in a TurboGears 2 project,
   you could define attribute in Gadget::

  need_project = True

Write A Simple Gadget
---------------------

Create a folder containing 2 files::

 setup.py
 gadget.py


in setup.py::

  from setuptools import setup, find_packages

  setup(
    name='HelloGadget',
    version="1.0",
    description='TurboGears2 Toolbox Gadget',
    author='Fred Lin',
    install_requires=[
    "ToolBox2",
    ],
    include_package_data=True,
    package_data={'':['gadget.py']},
    entry_points="""
    [turbogears2.toolboxcommand]
    hello = gadget:HelloGadget
    """
  )
  
in gadget.py::

  from toolbox2.lib.base import Controller
  from tg import expose

  class HelloGadget(Controller):
      """TurboGears ToolBox Gadget.
         Show Hello World in ToolBox
      """
      __label__ ="Hello"
      __version__ = "1.0"
      __author__ = "Fred Lin"
      __email__ = "mymail+tg2[at]gmail.com"
      __copyright__ = "Copyright 2008 Fred Lin"
      __license__ = "MIT"
      __group__ = "Help"
      __icon__ = "places/start-here.png"
      need_project = False
    
      @expose()
      def index(self):
          return 'Hello ToolBox'

Debugging
~~~~~~~~~

Run::

  $ python setup.py develop

or::

  $ python setup.py install

to register your project to setuptools. Then you could run 'paster
toolbox' to view your gadget!


Upload To Pypi
~~~~~~~~~~~~~~

Run::

  $ python setup.py register bdist_egg sdist --format=zip upload

to upload both egg and source code to pypi.

Remove Development Gadget
~~~~~~~~~~~~~~~~~~~~~~~~~

Run::

  $ easy_install -m hello

Check 'paster toolbox' list and the hello gadget is gone.

Future Plans
------------

 - Widget Browser gadget by ToscaWidget (Browse widgets)
 - upgrade MVC gadget with Source Highlight by ToscaWidget
 - upgrade MVC gadget with Editor function inspired by web2py
 - i18n Gadget
 - With Authorization
 - i18n
 - Model Designer Gadget rewrite with ToscaWidgets
 - Able to Custom tab
 - able to Manage tab
 - Able to custom app/tab

