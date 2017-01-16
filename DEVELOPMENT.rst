REST API SDK for SMS
====================

Some development documentation for the Python REST API SDK for SMS.

Release procedure
-----------------

The following steps are necessary to perform a release of the SDK:

1. Update to release version in ``clx/xms/__about__.py`` and
   ``docs/changelog.rst``.

3. Commit the changes and add a release tag.

4. Generate Sphinx docs and commit to ``gh-pages`` branch.

5. Prepare ``clx/xms/__about__.py`` and ``docs/changelog.rst`` for
   next development cycle.

6. Commit again.

7. Push it all to GitHub.

8. Build and upload the dist files to PyPI.
