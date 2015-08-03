JIRA Command Line Tool
=======================

This tool provides the capability to quickly react to issues found in a Production environment.

Installation
============

Download and install Python 2.7.10 if it is not already available and run::

pip install devprocess


Setup
=====

When running the first time setup defaults by::

./devprocess config --user=<jira-username> --password=<jira-password> --jira-url=<jira-url>
--project-name="Test EOS" --board-name="Test EOS" --triage-epic-name="Production Bugs"

Usage
=====

Report a Bug
------------
When a new "Blocker" high priority Bug is encountered in the Production environment enter::

./devprocess blocker --summary=<Issue encountered in Component X>
*Bug TE-8 created and assigned a priority of "Blocker"
This needs to be triage immediately. For help with triage enter:
./devprocess triage --help*

This will create a Bug and set:
* Project: Test EOS (from config above)
* Priority: Blocker

Triage
------

To Triage this ticket enter::

./devprocess triage TE-8 5 arahim
*Issue TE-8 Triaged successfully*

This will triage issue TE-8 by setting:
* Story Points: 5
* Assignee: arahim
* Epic Link: Production Bugs (Based on the config command above int eh Setup section)
* Sprint: <Current Active Sprint>

Help
====

To get help::

./devprocess --help

./devprocess blocker --help

./devprocess triage --help

Typical contents for this file would include an overview of the project, basic
usage examples, etc. Generally, including the project changelog in here is not
a good idea, although a simple "What's New" section for the most recent version
may be appropriate.
