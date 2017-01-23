REST API SDK for SMS
====================

Some development documentation for the Python REST API SDK for SMS.

Release procedure
-----------------

The following steps are necessary to perform a release of the SDK:

1. Update to release version in ``clx/xms/__about__.py`` and
   ``docs/changelog.rst``.

2. Commit the changes and add a release tag.

3. Generate Sphinx docs and commit to ``gh-pages`` branch.

4. Push it all to GitHub.

5. Package the library, e.g. using ``python setup.py sdist bdist_wheel``.

6. Sign and upload the dist files to PyPI, e.g. using
   ``twine upload -s dist/*``.

7. Prepare ``clx/xms/__about__.py`` and ``docs/changelog.rst`` for
   next development cycle.

8. Commit and push again.
