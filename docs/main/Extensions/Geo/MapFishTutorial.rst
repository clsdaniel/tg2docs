tgext.geo MapFish Tutorial
==========================


Introduction
------------

MapFish is a Web Application Framework for developing Geographic
Applications. It has two components, a server component and a client
component. The client component comprises a Javascript mapping toolkit
based on ExtJS and OpenLayers, whereas the server component is based
on the Pylons web framework. The MapFish server uses a set of paster
commands for creating controller and model code that make use of the
following components for providing a fully editable GIS vector layer
functionality.

    * SQLAlchemyGeom : Introduces a new data type (Geometry) in
      SQLAlchemy
    * Shapely : A python GIS library for manipulation of 2D geospatial
      geometries
    * GeoJSON : A JSON encoder / decoder for simple GIS features

tgext.geo makes use of modified paster commands that create model and
controller code for TG2 apps. The model uses reflection to map a
PostGIS table to the created model class. The controller is mounted on
the root controller and used for CRUD operations on the GIS database
using GeoJSON.


About This Tutorial
-------------------

In this tutorial we create a TG2 app and use the tgext.geo extension
to create a GIS vector layer. We also make use of tw.openlayers to
create a map with a WMS base layer and an overlay of vector data
retrieved from the tgext.geo backend.


Installation
------------

It is assumed that a fresh virtualenv has been created and TG2
installed following the :ref:`downloadinstall`. Install tgext.geo
using easy_install::

    (tg2env)$ easy_install -i http://www.turbogears.org/2.0/downloads/current/index tgext.geo

Make sure that tw.openlayers is installed::

    (tg2env)$ easy_install tw.openlayers

MapFish uses a PostGIS backend for storing Geographic data. Install
instructions for PostGIS can be found `here
<http://postgis.refractions.net/documentation/>_`. Additionally, we
need to install the following::

    (tg2env)$ easy_install -i http://www.turbogears.org/2.0/downloads/current/index egenix-mx-base
    (tg2env)$ easy_install -i http://www.turbogears.org/2.0/downloads/current/index psycopg2 


Creating A New TG2 App
----------------------

Create a new TG2 app with gis capability use the following paster
command::

    (tg2env)$ paster quickstart VectorApp --geo
    (tg2env)$ cd VectorApp


Create A MapFish Layers Config
------------------------------

Create a MapFish Layers config in the file layers.ini in the project
folder and add the necessary configuration. The layers.ini file should
have layer definitions as sections, e.g. [mylayer] followed by a
series of parameter value pairs in the *param=value* format. For this
example, we use a layer definition like this::

    [countries]
    singular=country
    db=gisdb
    table=world_fb
    epsg=4326
    units=degrees
    geomcolumn=the_geom
    idcolumn=Integer:gid

In the above example, a layer named countries would be created. The
*singular* param is used for creating the model class with the first
letter capitalized. In this case the model class would be *Country*
. The *db* should be a the PostGIS database and *table* the table name
to be mapped to the model class using database metadata reflection
(SQLAlchemy autoload feature). *epsg* should have the EPSG (European
Petroleum Survey Group) code for the desired datum and projection for
the geometry data. *geomcolumn* should have the name of the column
containing the geometry data. *idcolumn* should contain the data type
and name of the primary key column.


Creating The Geo Model And Controller
-------------------------------------

Once the layers.ini file has been created in the project folder, the
model and controller can be created by creating a new layer using the
following paster command::

    (tg2env)$ paster geo-layer countries

where countries is the new controller and should match the layer name
defined in the layers.ini file. Now edit the root controller
(package/controllers/root.py) to import the new controller and mount
it inside the RootController class::


    from vectorapp.controllers.countries import CountriesController

    class RootController(BaseController):
        countries = CountriesController()

The countries controller should now be accessible at the url location
`http://<host>:<port>/countries`.

Pointing the browser to the above url should show up all objects
(records) in the PostGIS table as JSON (GeoJSON).


Displaying The Vector Data As A Layer In An OpenLayers Map
----------------------------------------------------------

We are now ready to access the vector data from the PostGIS spatial
database using the new countries controller. We now need to use the
tw.openlayers ToscaWidgets Library to create a map and use the data
returned by the countries controller as a vector layer in the map. We
also make use of some OpenLayers based javascript code to select
features on mouse hover and display them in the sidebar div.


Initialize The Widgets In Controller
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The tw.openlayers has library of widgets for creating Map, Layers and
Controls using OpenLayers. The following paragraphs show how the
layers, controls and the map widgets are initialized. First we need to
import the necessary symbols from the ToscaWidgets and the
tw.openlayers API::

    from tw.api import WidgetsList, js_symbol
    from tw.openlayers import Map, GML, WMS, LayerSwitcher, OverviewMap, \
                        MouseToolbar, MousePosition, PanZoomBar, \
                        Permalink, SelectFeature

We create the layers as a WidgetsList which contains several
layers. Our data would be fetched into the *transportation* layer
which is defined as a GML (Geography Markup Language) layer. In
OpenLayers the GML layer is used to create a vector layer using data
obtained in specific vector formats. In this case, the option *format:
OpenLayers.Format.GeoJSON* indicates that our data would be in GeoJSON
format. Note the use of *js_symbol* function used from the
ToscaWidgets API. This is useful in passing Javascript symbols to the
encapsulated Javascript code. Otherwise the expression would get
passed as a string. The *url* parameter of GML specifies the url to be
used to fetch the data. In this case a relative path to the countries
controller is specified::

    class MyLayers(WidgetsList):
        ol = WMS(name="OpenLayers WMS",
            url=["http://labs.metacarta.com/wms/vmap0"],
            options = {'layers':'basic'})
        nasa = WMS(name="NASA Global Mosaic",
            url=['http://t1.hypercube.telascience.org/cgi-bin/landsat7'],
            options={'layers': 'landsat7'})
        transportation = GML(name="Transportation", url="countries",
            options = {
                "format": js_symbol(" OpenLayers.Format.GeoJSON"),
                "isBaseLayer": False,
                "projection": js_symbol(' new OpenLayers.Projection("EPSG:4326")')
            })

We have to also initialize the required controls as a WidgetsList. Out
of these the SelectFeature is the most interesting in this
example. Feature selection takes place on hovering the mouse over the
feature geometry as specified by the *"hover": True* option. The
Javascript custom functions *show_info()* and *erase_info()* would be
called respectively when a feature is selected or unselected::

    class MyControls(WidgetsList):
        ls = LayerSwitcher()
        ovm = OverviewMap()
        mtb = MouseToolbar()
        mp = MousePosition()
        pzb = PanZoomBar()
        pl = Permalink()
        sf = SelectFeature(layer_name="Transportation", options={
                "hover": True,
                "onSelect": js_symbol("show_info"),
                "onUnselect": js_symbol("erase_info")})

The Map widget is initialized using the layers and controls
initialized earlier::

    mymap = Map(id="map", layers=MyLayers(), controls=MyControls(),
                                center=(15,0), zoom=3)

Finally, we use the Map widget inside the controller method to stick
it to the template context::

    class RootController(BaseController):
        countries = CountriesController()

        @expose('geogrid.templates.index')
        def index(self):
            pylons.c.map = mymap
            return dict(page='index')


Adding The Style Code
~~~~~~~~~~~~~~~~~~~~~

The following stylesheet code may be added to suite the map display::

   <style>
   #map {
       width: 480px;
       height: 480px;
       border: 2px solid #0000ff;
       float: left;
   }
   </style>

Define The Javascript Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We had called two custom Javascript functions on feature select and
unselect. These functions could be either included within a pair of
<script> tags in the head section of index.html template or included
as a file placed at the *package*/public/javascript folder::

    <script type="text/javascript">
        function show_info (feature) {
            $("sb_top").innerHTML = "<BR/><b>Country : " + feature.attributes.country +
                  "<BR/></b>Airports : " + feature.attributes.airports +
                  "<BR/>Roadways : " + feature.attributes.roadways +
                  "<BR/>Railways : " + feature.attributes.railways +
                  "<BR/>Waterways : " + feature.attributes.waterways;
        }

        function erase_info(feature) {
            $("sb_top").innerHTML = "<br />Select a country by hovering the mouse over it.";
        }
    </script>


Add The Widget In The HTML Body
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The template HTML code would be modified to render the map by calling
the widget from the template context::

    <body>
      ${sidebar_top()}
      ${tmpl_context.map()}
      <div class="clearingdiv" />
      <div class="notice"> Thank you for choosing TurboGears.
      </div>
    </body>

See tgext.geo And tw.openlayers In Action
-----------------------------------------

Its time to see tgext.geo and tw.openlayers in action now. Run the
paster command to start the local HTTP server::

    (tg2env)$ paster serve --reload development.ini

Point your browser to http://localhost:8080 to view the map. Moving
the mouse over the countries shows data about the country in the
*sidebar_top* div element.
