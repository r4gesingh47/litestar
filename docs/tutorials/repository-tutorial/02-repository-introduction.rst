Interacting with repositories
-----------------------------
Now that we've covered the modeling basics, we are able to create our first repository
class.  The repository classes includes all of the standard CRUD operations as well as a
few advanced features such as pagination, filtering and bulk operations.

Before we jump in to the code, let's take a look at the available functions available in
the the synchronous and asynchronous repositories.

+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|      Function       |    Category    |                                                                                                                 Description                                                                                                                 |
+=====================+================+=============================================================================================================================================================================================================================================+
| ``get``             | Selecting Data | Select a single record by primary key. Raising an exception when no record is found.                                                                                                                                                        |
+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``get_one``         | Selecting Data | Select a single record specified by the ``kwargs`` parameters. An exception is raised when no record is found.                                                                                                                              |
+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``get_one_or_none`` | Selecting Data | Select a single record specified by the ``kwargs`` parameters. Returns ``None`` when no record is found.                                                                                                                                    |
+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``list``            | Selecting Data | Select a list of records specified by the ``kwargs`` parameters. Optionally it can be filtered by the included ``FilterTypes`` args.                                                                                                        |
+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``list_and_count``  | Selecting Data | Select a list of records specified by the ``kwargs`` parameters. Optionally it can be filtered by the included ``FilterTypes`` args. Results are returned as a 2 value tuple that includes the rows selected and the total count of records |
+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``get_or_create``   | Creating Data  | Get a record specified by the the ``kwargs`` parameters.  If no record is found, one is created with the given values.  There's an optional attribute to filter on a subset of the supplied parameters and to merge updates.                |
+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``create``          | Creating Data  | Create a new record in the database.                                                                                                                                                                                                        |
+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``create_many``     | Creating Data  | Create one or more rows in the database.                                                                                                                                                                                                    |
+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``update``          | Updating Data  | Update an existing record in the database.                                                                                                                                                                                                  |
+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``update_many``     | Updating Data  | Update one or more rows in the database.                                                                                                                                                                                                    |
+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``upsert``          | Updating Data  | A single operation that updates or inserts a record based whether or not the primary key value on the model object is populated.                                                                                                            |
+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``remove``          | Removing Data  | Remove a single record from the database.                                                                                                                                                                                                   |
+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``remove_many``     | Removing Data  | Remove one or more records from the database.                                                                                                                                                                                               |
+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


.. note::

    - All three of the bulk DML operations will leverage dialect-specific enhancements
      to be as efficient as possible. In addition to using efficient bulk inserts binds,
      the repository will optionally leverage the multi-row ``RETURNING`` support where
      possible. The repository will automatically detect this support from the
      SQLAlchemy driver, so no additional interaction is required to enable this.

    - SQL engines generally have a limit to the number of elements that can be appended
      into an `IN` clause. The repository operations will automatically break lists that
      exceed this limit into multiple queries that are concatenated together before
      return. You do not need to account for this in your own code.


In the following examples, we'll cover a few ways that you can use the repository within
your applications.


Model Repository
^^^^^^^^^^^^^^^^

Here we import the
:class:`SQLAlchemyAsyncRepository <litestar.contrib.sqlalchemy.repository.SQLAlchemyAsyncRepository>`
class and create an ``AuthorRepository`` repository class. This is all that's required
to include all of the integrated repository features.

.. literalinclude:: /examples/contrib/sqlalchemy/sqlalchemy_repository_crud.py
    :language: python
    :caption: app.py
    :emphasize-lines: 25-28
    :linenos:

Repository Context Manager
^^^^^^^^^^^^^^^^^^^^^^^^^^

Since we'll be using the repository outside of a Litestar application in this script,
we'll make a simple context manager to automatically handle the creation (and cleanup)
of our Author repository.

The ``repository_factory`` method will do the following for us:
    - Automatically create a new DB session from the SQLAlchemy configuration.
    - Rollback session when any exception occurs
    - Automatically commit after function call completes.


.. literalinclude:: /examples/contrib/sqlalchemy/sqlalchemy_repository_crud.py
    :language: python
    :caption: app.py
    :emphasize-lines: 39-47
    :linenos:


Creating, Updating and Removing Data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To illustrate a few ways you can manipulate data in your database, we'll go through the
various CRUD operations:

Creating Data: Here's a simple insert operation to populate our new Author table

    .. literalinclude:: /examples/contrib/sqlalchemy/sqlalchemy_repository_crud.py
        :language: python
        :caption: app.py
        :emphasize-lines: 50-54
        :linenos:

Updating Data: The ``update`` method will ensure any updates made to the model object are executed on the database

    .. literalinclude:: /examples/contrib/sqlalchemy/sqlalchemy_repository_crud.py
        :language: python
        :caption: app.py
        :emphasize-lines: 57-61
        :linenos:

Removing Data: The ``remove`` method accepts the primary key of the row you want to delete

    .. literalinclude:: /examples/contrib/sqlalchemy/sqlalchemy_repository_crud.py
        :language: python
        :caption: app.py
        :emphasize-lines: 64-68
        :linenos:

Now that we've seen how to do single-row operations, let's look at the bulk methods we
can use.


Working with Bulk Data Operations
---------------------------------
In this section, we delve into the powerful capabilities of the repository classes for
handling bulk data operations. Our example illustrates how we can efficiently manage
data in our database. Specifically, we'll use a JSON file containing information about
US states and their abbreviations.

Here's what we're going to cover:

Fixture Data Loading
^^^^^^^^^^^^^^^^^^^^

We will introduce a method for loading fixture data. Fixture data is sample data that
populates your database and helps test the behavior of your application under realistic
conditions. This pattern can be extended and adjusted to meet your needs.

.. literalinclude:: /examples/contrib/sqlalchemy/sqlalchemy_repository_bulk_operations.py
    :language: python
    :caption: app.py
    :emphasize-lines: 37-55
    :linenos:

You can review the JSON source file here:

.. literalinclude:: /examples/contrib/sqlalchemy/us_state_lookup.json
    :language: json
    :caption: us_state_lookup.json


Bulk Insert
^^^^^^^^^^^

We'll use our fixture data to demonstrate a bulk insert operation. This operation allows
you to add multiple records to your database in a single transaction, improving
performance when working with larger data sets.

.. literalinclude:: /examples/contrib/sqlalchemy/sqlalchemy_repository_bulk_operations.py
    :language: python
    :caption: app.py
    :emphasize-lines: 68-69
    :linenos:


Paginated Data Selection
^^^^^^^^^^^^^^^^^^^^^^^^

Next, let's explore how to select multiple records with pagination. This functionality
is useful for handling large amounts of data by breaking the data into manageable
'pages' or subsets.  ``LimitOffset`` is one of several filter types you can use with the
repository.

.. literalinclude:: /examples/contrib/sqlalchemy/sqlalchemy_repository_bulk_operations.py
    :language: python
    :caption: app.py
    :emphasize-lines: 74-75
    :linenos:


Bulk Delete
^^^^^^^^^^^

Here we demonstrate how to perform a bulk delete operation. Just as with the bulk
insert, deleting multiple records with the batch record methods is more efficient than
executing row-by-row.

.. literalinclude:: /examples/contrib/sqlalchemy/sqlalchemy_repository_bulk_operations.py
    :language: python
    :caption: app.py
    :emphasize-lines: 77-79
    :linenos:

Counts
^^^^^^

Finally, we'll demonstrate how to count the number of records remaining in the database.

.. literalinclude:: /examples/contrib/sqlalchemy/sqlalchemy_repository_bulk_operations.py
    :language: python
    :caption: app.py
    :emphasize-lines: 81-83
    :linenos:

Now that we have demonstrated how to interact with the repository objects outside of a
Litestar application, our next example will use dependency injection to add this
functionality to a :class:`~litestar.controller.Controller`!
