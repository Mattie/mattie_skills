# RMDD tests

`test_receipt_helper.py` exercises the RMDD receipt helper directly.

The `fixtures/` and `subagentic/` directories contain isolated project
workspaces used to exercise the coordinated skills. Their internal tests belong
to those fixture projects, so repository-wide pytest discovery excludes both
directories.

Copy a fixture to a temporary directory and initialize that copy as its own Git
repository before running RMDD against it. Running a fixture in place would make
the enclosing `mattie_skills` work tree the RMDD project root.
