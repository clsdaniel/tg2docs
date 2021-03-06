

tgext.geo FeatureServer Tutorial
================================


Introduction
------------

FeatureServer is a simple Python-based geographic feature server. It
allows you to store geographic vector features in a number of
different backends, and interact with them -- creating, updating, and
deleting -- via a REST-based API. It is distributed under a BSD-like
open source license.

The text.geo.featureserver module enables easy integration of
featureserver into TurboGears2 apps by providing the following:

* GeoAlchemy Datasource - This allows geographic features to be stored
  in any of the spatial databases supported by GeoAlchemy_.
* FeatureServer Controller - This creates a new controller that reads
  the config and makes use of the FeatureServer API to dispatch
  requests to featureserver.

About This Tutorial
-------------------

In this tutorial we will create a TG2 app and use the tgext.geo
extension to configure, store, manipulate and retreive GIS features in
a PostGIS database.


Installation
------------

It is assumed that a fresh virtualenv has been created and TG2
installed following the :ref:`downloadinstall`. Install
tgext.geo using easy_install::

    (tg2env)$ easy_install -i http://www.turbogears.org/2.0/downloads/current/index/ tgext.geo

We assume that a PostgreSQL server is installed and ready for
use. Install PostGIS_ and create a new PostGIS_ enabled database
called `gis`. Refer to the `PostGIS docs`_ to achieve this. We also
need to install GeoAlchemy and the python db-api for postgres::

    (tg2env)$ easy_install GeoAlchemy egenix-mx-base psycopg2

Download and install featureserver from the svn repo::

    (tg2env) $ svn co http://svn.featureserver.org/trunk/featureserver featureserver
    (tg2env) $ cd featureserver
    (tg2env) $ python setup.py install


Creating A New TG2 App
----------------------

Create a new TG2 app named "TGFeature" with gis capability::

    (tg2env)$ paster quickstart TGFeature --geo
    (tg2env)$ cd TGFeature
    (tg2env)$ python setup.py develop


Model Definition For Features
-----------------------------

We assume that we have to model a layer of roads in our
application. We open the tgfeature/model/__init__.py file in the
package and add the following model definition::

    from datetime import datetime
    from sqlalchemy import Column, Integer, Unicode, DateTime
    from geoalchemy import GeometryColumn, LineString
    from geoalchemy import GeometryDDL

    class Road(DeclarativeBase):
        __tablename__ = 'roads'
        id = Column(Integer, primary_key=True)
        name = Column(Unicode, nullable=False)
        width = Column(Integer)
        created = Column(DateTime, default=datetime.now())
        geom = GeometryColumn(LineString(2))

    GeometryDDL(Road.__table__)

Apart from the standard attributes, we have defined a spatial
attribute called `geom` as a `GeometryColumn`. We will use this
attribute to store geometry values of data type `LineString` in the
database. GeoAlchemy supports other geometry types such as Point,
Polygon and Mutiple Geometries. We also pass the dimension of the
geometry as a parameter. The Geometry type takes another parameter for
the `SRID`, the Spatial Reference ID. In this case we leave it to its
default value of `4326` which means that our geometry values will be
expressed in geographic latitude and longitude coordinate
system. There is a nice blogpost on `SharpGIS`_ that explains the
concept of SRID.  EPSG:4326 is chosen as the default SRID by PostGIS
and other software primarily because it is based on the global
ellipsoid (called WGS84) which is not specific to a particular region
or continent.

We finally call the GeometryDDL DDL Extension that enables creation
and deletion of geometry columns just after and before table create
and drop statements respectively. The GeometryColumn, LineString and
GeometryDDL must be imported from the geoalchemy package.

	  
Creating Tables In The Database 
-------------------------------

The database tables can now be created using the setup-app paster
command

.. code-block:: bash

    $ (tg2env) paster setup-app development.ini

In case we need sample data to be inserted during application startup,
we must add the sample data into the setup script,
i.e. tgfeature/websetup.py prior to running the setup command. Let us
add some sample data.

.. code-block:: python

    from geoalchemy import WKTSpatialElement
    wkt = "LINESTRING(-80.3 38.2, -81.03 38.04, -81.2 37.89)"
    road1 = model.Road(name="Peter St", width=6, geom=WKTSpatialElement(wkt))
    wkt = "LINESTRING(-79.8 38.5, -80.03 38.2, -80.2 37.89)"
    road2 = model.Road(name="George Ave", width=8, geom=WKTSpatialElement(wkt))
    model.DBSession.add_all([road1, road2])



FeatureServer Config
--------------------

Now we need to configure our app by declaring certain parameters under
the [app:main] section of the ini file. In this case we use
development.ini as we are in development mode right now.

.. code-block:: python

    geo.roads.model=tgfeature.model
    geo.roads.cls=Road
    geo.roads.table=roads
    geo.roads.fid=id
    geo.roads.geometry=geom

The config parameters use a geo.<layer>.param=value format. This
allows additional layers to be defined within the same app as follows:

.. code-block:: python

    geo.lakes.model=tgfeature.model
    geo.lakes.cls=Lake
    geo.lakes.table=lakes
    geo.lakes.fid=id
    geo.lakes.geometry=geom

In this tutorial, however, we will use only the roads layer.

Using The FeatureServerController
---------------------------------

We can now import and mount the FeatureServer Controller inside our
root controller.

.. code-block:: python

    from tgfeature.model import DBSession
    from tgext.geo.featureserver import FeatureServerController

    class RootController(BaseController):
        ....
        roads = FeatureServerController("roads", DBSession)

We pass two parameters here. The first one being the layer name. This
must be the same as layer name used in development.ini. The second
parameter is the sqlalchemy session. In case we were using the lakes
layer too, as shown in the sample config, we would create two
controller instances as:

.. code-block:: python

    class RootController(BaseController):
        ....
        roads = FeatureServerController("roads", DBSession)
        lakes = FeatureServerController("lakes", DBSession)

Testing The Server Using Curl
-----------------------------

We are now ready to start and test out new geo-enabled TG2 app. Start
the server in development mode by running:

.. code-block:: bash

    $(tg2env) paster serve --reload development.ini

Note the `--reload` option. This tells the server to reload the app
whenever there is a change in any of the package files that are in its
dependency chain. Now we will open up a new command window and test
the server using the `curl` utility.

.. code-block:: bash

    # Request the features in GeoJSON format (default)
    $ curl http://localhost:8080/roads/all.json
    or simply
    $ curl http://localhost:8080/roads
    {"crs": null, "type": "FeatureCollection", .... long GeoJSON output

    # Request the features in GML format
    $ curl http://localhost:8080/8080/roads/all.gml
    <wfs:FeatureCollection
   	xmlns:fs="http://example.com/featureserver
        ....   long GML output

    # Request the features in KML format
    $ curl http://localhost:8080/roads/all.kml
    <?xml version="1.0" encoding="UTF-8"?>
        <kml xmlns="http://earth.google.com/kml/2.0"
        ....  long KML output

Now lets create a new feature using curl. Store the following json
data in a new file postdata.json:

.. code-block:: javascript

    {"features": [{
        "geometry": {
            "type": "LineString",
            "coordinates": [[-88.913933292993605, 42.508280299363101],
                            [-88.8203027197452, 42.598566923566899],
                            [-88.738375968152894, 42.723965012738901],
                            [-88.611305904458604, 42.968073292993601],
                            [-88.365525649681501, 43.140286668789798]
            ]
        },
        "type": "Feature",
        "id": 10,
        "properties": {"name": "Broad Ave", "width": 10}
    }]}

Create a POST request using this data and send it to the server.

.. code-block:: bash

    $(tg2env) curl -d @postdata.json http://localhost:8080/roads/create.json

This creates a new feature and returns back the features in json
format. To modify the feature edit the postdata.json file and change
the properties. Lets change the name property from `Broad Ave` to
`Narrow St` and the width property from `10` to `4`. The modify url
should include the feature id as shown below:

.. code-block:: bash

    $(tg2env)  curl -d @postdata.json http://localhost:8080/roads/3.json

The data can be requested in JSON, GML, KML and ATOM formats by using
the apprpriate suffix, i.e. 3.json, 3.gml, 3.kml or 3.atom
respectively.  JSON is the default content type resturned by
featureserver, so using it without any suffix (e.g. roads/3) returns
data in GeoJSON format.  For deleting the feature simply send a DELETE
request with the feature id in the url:

.. code-block:: bash

    $(tg2env) curl -X DELETE http://localhost:8080/roads/3.json

An OpenLayers Application Using FeatureServer
---------------------------------------------

The server is now ready to be accessed by client applications for
storing, manipulating and deleting featues. OpenLayers_ is an open
source javascript web mapping application. It is quite mature and is
under active development. To develop an OpenLayers web application
using featureserver the developer is strongly recommended to have a
look at the demo application available with the featureserver source
code. Copy the demo app (index.html inside featureserver source code
directory) to the public folder under a different name:

.. code-block:: bash

    $(tg2env) cp /path/to/featureserversource/index.html tgfeature/public/demo.html
    $(tg2env) cp /path/to/featureserversource/json.html tgfeature/public/
    $(tg2env) cp /path/to/featureserversource/kml.html tgfeature/public/

Now modify these files to change the following::

    * change all references to featureserver.cgi to '' (null)
    * change all references to scribble to 'roads' (layer)

Point your browser to http://localhost:8080/demo.html. You should now
be able to view, create and modify features using featureserver
running inside your TG2 app.

Adding Authentication and Authorization
---------------------------------------

TG2 supports authentication and authorization using the repoze.who and
repoze.what packages along with other packages in these namespaces.  A
TG2 app created using the authentication and authorization option
(default) has these packages already included and configured as WSGI
middleware.

By default TG2 uses SQLAlchemy based authentication and authorization,
where the user credentials and authorization roles / permissions are
maintained in database tables. There are plugins available to support
other authentication mechanisms such as LDAP based auth, OpenID based
auth, etc.  Refer to the Authentication and Authorization docs for
details.

At the moment only controller wide authorization control is available in
tgext.geo. In order to have authorization, pass a repoze.what authorization
predicate as an additional parameter to FeatureServerController:

.. code-block:: python

    from tg.i18n import ugettext as _, lazy_ugettext as l_
    from repoze.what import predicates
    from tgext.geo.featureserver import FeatureServerController

    class RootController(BaseController):

        allow_only = predicates.has_permission('feature',
                    msg=l_('Only for people with "feature" permission'))
        roads = FeatureServerController("roads", DBSession, allow_only)

Now we must go to the admin interface and define a new permission
called "feature". Once defined, this permission must be granted to
groups and/or users to whom this new controller is now restricted.

.. _GeoAlchemy: http://geoalchemy.org
.. _PostGIS: http://postgis.refractions.net/
.. _`PostGIS docs`: http://postgis.refractions.net/documentation/
.. _SharpGIS: http://www.sharpgis.net/post/2007/05/Spatial-references2c-coordinate-systems2c-projections2c-datums2c-ellipsoids-e28093-confusing.aspx
.. _OpenLayers: http://openlayers.org
