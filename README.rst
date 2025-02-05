================
Flask Hypermedia
================

This is a set of ulities for building `hypermedia-driven applications <https://hypermedia.systems/book/contents/>`_ with Flask.

This relies on two underlying technologies:

1. `HTMX <https://htmx.org/>`_, a JavaScript library that extends HTML as a hypertext (via the server-side library `flask-htmx <https://pypi.org/project/flask-htmx/>`_)
2. `HAL <https://www.apigility.org/documentation/api-primer/halprimer>`_, a standard for embedding hypermedia controls in JSON data

The underlying goals are:

* Implement applications that fully satisfy the REST API design philosophy
* Focus on server-side code rather than client-side code or SPAs (do as little client-side as possible!)
* Return either human-oriented HTML or machine-oriented JSON from the same endpoints, with minimal duplication of code


Rough Concept
-------------

I envision an application using this library to work something like this:

.. code-block:: python

    from flask_hypermedia import Hypermedia, Resource, make_response

    hyper = Hypermedia(app)

    @app.route('/some/resource')
    def some_resource():
        # All requests build resources
        resource = Resource.for_request(data=get_from_database())
        # Links are determined by the user permissions and the current state of the resource
        if has_permission(user, Permissions.edit):
            resource.link('edit', url_for('edit_some_resource'))
        # Use headers to determine what kind of response to return
        if hyper.wants_json:
            return resource.to_hal()
        else:
            return render_template('some_resource', resource=resource)

.. code-block:: jinja2
    
    {# Optionally include the full layout if not an HTMX request #}
    {% if not hyper.htmx %}{% extends 'layout.jinja2' %}{% endif %}
    {# Data is stored in the resource #}
    <h1>Here are the things</h1>
    <p>{{ resource.data.thing1 }}</p>
    <p>{{ resource.data.thing2 }}</p>
    {# Helpers to render links and forms, if and only if they exist in the resource (meaning less logic in templates!) #}
    {{ resource.links.edit | to_a(class='button') }}