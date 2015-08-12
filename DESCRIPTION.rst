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

    > devproc config <jira-username> <jira-password> <jira-project-name> <jira-agile-board-name>

Usage
=====

Report a Bug
------------
When a new "Blocker" high priority Bug is encountered in the Production environment enter::

    > devproc blocker "Details of issue encountered in Component X which will be added to the jira issue summary"
    Bug TE-8 created and assigned a priority of "Blocker"
    This needs to be triage immediately. For help with triage enter:
    devproc triage --help

This will create a Bug and set:

* Project: <jira-project-name> (from the config above)
* Priority: Blocker

Triage
------

To Triage this ticket enter::

    > devproc triage TE-8 5 arahim
    *Issue TE-8 Triaged successfully*

This will triage issue TE-8 by setting:
* Story Points: 5
* Assignee: arahim
* Epic Link: [Ongoing] Production Bugs (This is the default setting. To change it look at "devproc config --help")
* Sprint: <Current Active Sprint> (If there is not active sprint this will not be set)

Help
====

To get help::

> devproc --help

> devproc blocker --help

> devproc triage --help
