#!/usr/bin/env python
import argparse
import os
from jira import JIRA
import ConfigParser
import keyring
import sys
import json

#TODO: Do all of these
# tests (unit/functional)
# logging
# package/install (PyPy)
# refactor (config/init command)
# Implement an "update" command that can get all field names and update a JIRA issue accordingly (objects, strings etc)

#TODO: Move these defaults to config file
CONFIG_FILE_PATH = os.path.join(os.path.expanduser("~"), ".devconfig")

#defaults if not provided
JIRA_URL = "http://jira"

#TODO - Read from setup.py
KEYRING_SERVICE_NAME = "devprocess"
#PROJECT_NAME = "Test EOS"
#BOARD_NAME = "Test EOS"
#EPIC_NAME = "[Ongoing] Production Bugs"
TRIAGE_PRIORITY_BLOCKER_NAME = "Blocker"
BUG_TYPE_NAME = "Bug"
EPIC_TYPE_NAME = "Epic"
#DEFAULT_ASSIGNEE_NAME = "arahim"

#TODO: convert this to a decorator
def is_configured():
    if not os.path.isfile(CONFIG_FILE_PATH):
        print "Unable to proceed. Configuration has not been performed. For help on confguration enter:\n" \
              "'devproc config --help'"
        return False
    return True

def get_jira_connection(url, user):

    password = keyring.get_password(KEYRING_SERVICE_NAME, user)

    try:
        jira = JIRA(url, basic_auth=(user, password))
    except Exception as e:
        if e.status_code == 403:
            print "Unable to connect to JIRA. Check the jira-url, user and password. Try again.\n"
            raise

        print "Make sure you are on VPN or can get to your JIRA server from this network"
        raise

    return jira

def config(args):
    #store in config file
    #print args
    #store password in keyring
    keyring.set_password(KEYRING_SERVICE_NAME, args.user, args.password)

    #validate config settings
    print "Validating configuration parameters..."

    jira = get_jira_connection(args.jira_url, args.user)

    project = next((b for b in jira.projects() if b.name == args.projectname), None)
    if not project:
        print 'Unable to find project named "{0}". Ensure that it exists and try again.'.format(args.projectname)
        return

    board = next((b for b in jira.boards() if b.name == args.boardname), None)
    if not board:
        print 'Unable to find an Agile board named "{0}"". Check and try again.'.format(args.boardname)
        return

    # TODO: Get and store all required field names
    priority_field_name = None
    story_points_field_name = None
    epic_links_field_name = None
    epic_name_field_name = None
    sprint_field_name = None
    epic = None
    priority_blocker = None

    for field in jira.fields():
        if field["name"] == "Priority":
            priority_field_name = field["id"]
        if field["name"] == "Story Points":
            story_points_field_name = field["id"]
        if field["name"] == "Epic Link":
            epic_links_field_name = field["id"]
        if field["name"] == "Epic Name":
            epic_name_field_name = field["id"]
        if field["name"] == "Sprint":
            sprint_field_name = field["id"]

    for p in jira.priorities():
        if p.name == TRIAGE_PRIORITY_BLOCKER_NAME:
            priority_blocker = p
            break

    if not priority_blocker:
        print 'Could not find a priority named "Blocker". Ensure it exists and try again.\n'
        return

    epic_issue = None

    epic_issues = jira.search_issues("Project = '{0}' AND issueType = 'Epic' AND 'Epic Name' = '{1}'".format(
        args.projectname, args.epic_name))

    if epic_issues:
        epic_issue = epic_issues[0]

    if not epic_issue:
        epic_data = {
            epic_name_field_name: args.epic_name,
            "summary": args.epic_name,
            "issuetype": { "name": EPIC_TYPE_NAME },
            "project": project.key
        }

        print 'Could not find an Epic named "{0}". Creating it..."\n'.format(args.epic_name)

        try:
            epic_issue = jira.create_issue(epic_data)
        except:
            print "Failure: Unable to create epic named {0}. Create the epic in project {1} and try again.".format(
                args.epic_name, args.projectname)
            return

        print "Created epic."


    #save to file
    config = ConfigParser.RawConfigParser()

    config.add_section("Defaults")
    config.set("Defaults", "user", '"{0}"'.format(args.user))
    config.set("Defaults", "jira_url", '"{0}"'.format(args.jira_url))
    config.set("Defaults", "project_name", '"{0}"'.format(args.projectname))
    config.set("Defaults", "board_name", '"{0}"'.format(args.boardname))
    config.set("Defaults", "epic_name", '"{0}"'.format(args.epic_name))
    config.set("Defaults", "epic_key", '"{0}"'.format(epic_issue.key))


    config.add_section("Internal Field IDs")
    config.set("Internal Field IDs", '"Priority"', '"{0}"'.format(priority_field_name))
    config.set("Internal Field IDs", '"Story Points"', '"{0}"'.format(story_points_field_name))
    config.set("Internal Field IDs", '"Epic Links"', '"{0}"'.format(epic_links_field_name))
    config.set("Internal Field IDs", '"Epic Name"', '"{0}"'.format(epic_name_field_name))
    config.set("Internal Field IDs", '"Sprint"', '"{0}"'.format(sprint_field_name))
    config.set("Internal Field IDs", "priority_blocker_id", '"{0}"'.format(priority_blocker.id))


    #store password in keyring
    #keyring.set_password(KEYRING_SERVICE_NAME, args.user, args.password)

    with open(CONFIG_FILE_PATH, "w") as f:
        config.write(f)

    print "Default Configuration set succesfully in {0}".format(CONFIG_FILE_PATH)

def get_config():

    """

    :rtype : Dict
    """
    config = ConfigParser.SafeConfigParser()
    config.read(CONFIG_FILE_PATH)

    config_data = {}

    for s in config.sections():
        for i in config.items(s):
            config_data[i[0].strip('"')] = i[1].strip('"')

    #print config_data

    return config_data

def triage(args):

    if not is_configured():
        return

    issue_key = args.issuekey
    story_points = args.storypoints
    assignee_name = args.assignee

    config_data = get_config()

    user = config_data["user"]
    jira_url = config_data["jira_url"]
    project_name = config_data["project_name"]
    board_name = config_data["board_name"]
    priority_blocker_id = config_data["priority_blocker_id"]

    priority_field_name = config_data["priority"]
    #TODO: "epic_name" can be confused with "epic name" but these are different values
    epic_links_field_name = config_data["epic links"]
    epic_key = config_data["epic_key"]
    story_points_field_name = config_data["story points"]
    sprint_field_name = config_data["sprint"]

    jira = get_jira_connection(jira_url, user)
    
    #jira =  JIRA(JIRA_URL, basic_auth=(args.user, args.password))
    issue = jira.issue(issue_key)


    
    board_id = None
    for board in jira.boards():
        if board.name == board_name:
            board_id = board.id
            break
    
    if not board_id:
        print 'Unable to proceed. Did not find board "{0}". Ensure that this board exists and run:\n' \
              'devproc config --help'.format(board_name)
        return


    data = {}
    #Issue with JIRA API that causes a 500 error if fields are already set
    #Only update fields that are not set correctly
    if getattr(issue.fields(), priority_field_name).id != str(priority_blocker_id):
        data[priority_field_name] = { "id": str(priority_blocker_id) }

    if getattr(issue.fields(), epic_links_field_name) != epic_key:
        data[epic_links_field_name] = epic_key

    if getattr(issue.fields(), story_points_field_name) != story_points:
        data[story_points_field_name] = story_points

    #get the current Sprint - DO NOT move this to a config file as this will change often
    #record but proceed if active sprint does not exist
    sprint_id = None
    for sprint in jira.sprints(board_id, True):
        if sprint.state == "ACTIVE":
            sprint_id = sprint.id
            break

    if not sprint_id:
        print "Could not find an active sprint. Proceeding with triage but the Issue will not be assigned to a sprint."

    #if sprint exists and is already assigned
    is_sprint_assigned = False
    if sprint_id:
        sprints =  getattr(issue.fields(), sprint_field_name)
        if sprints:
            for sprint in sprints:
                if sprint.split("id=")[-1].strip("]") == str(sprint_id):
                    is_sprint_assigned = True
                    break

    if sprint_id and (not is_sprint_assigned):
        #if getattr(issue.fields(), sprint_field_name)[0].split("id=")[-1].strip("]") != str(sprint_id):
        data[sprint_field_name] = str(sprint_id)

    #TODO: Validate that assignee exists as a user in JIRA otherwise fail it
    is_assigned = False
    if issue.fields().assignee:
        if issue.fields().assignee.name == assignee_name:
            is_assigned = True
    
    if not is_assigned:
        data["assignee"] = { "name": assignee_name }
    
    #TODO: add a debug log and write the following to it
    #print data

    issue.update(fields=data)

    print "Issue {0} Triaged successfully".format(issue.key)


def blocker(args):

    if not is_configured():
        return

    summary = args.summary

    config_data = get_config()

    user = config_data["user"]

    jira_url = config_data["jira_url"]

    project_name = config_data["project_name"]

    #print jira_url, user, password

    jira = get_jira_connection(jira_url, user)
    #jira =  JIRA(jira_url, basic_auth=(user, password))

    project_key = next((p.key for p in jira.projects() if p.name == project_name), None)

    if not project_key:
        print 'Unable to find project "{0}". Failed to create a new issue.'.format(project_name)
        return

    data = {
        "project": project_key,
        "issuetype": { "name": BUG_TYPE_NAME },
        "priority": { "name": TRIAGE_PRIORITY_BLOCKER_NAME },
        #"assignee": { "name": DEFAULT_ASSIGNEE_NAME },
        "summary": summary

    }

    issue = jira.create_issue(data)

    print 'Bug {0} created and assigned a priority of "Blocker"\n' \
            'This needs to be triaged immediately. For help with triage enter: \n' \
            'devproc triage --help'.format(issue.key)
    

def parse_arguments():

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    sub_parsers = parser.add_subparsers()

    #define the config command
    #requiredNamed = sub_parsers.add_argument_group('required named arguments')
    parser_config = sub_parsers.add_parser("config", help="Required named arguments to set defaults.")
    #parser_config = sub_parsers.add_parser("config", help="Required named arguments to set defaults.")
    parser_config.add_argument("user", help="JIRA username")
    parser_config.add_argument("password", help="JIRA password")
    parser_config.add_argument("projectname", help="JIRA Project Name")
    parser_config.add_argument("boardname", help="JIRA Agile Board name")
    parser_config.add_argument("-j", "--jira-url", default="http://jira", help='(default: "%(default)s")', metavar="")
    parser_config.add_argument("-e", "--epic-name", default="[Ongoing] Production Bugs",
        help='epic name for triaged bugs (default: "%(default)s")', metavar="")
    parser_config.set_defaults(func=config)

    parser_triage = sub_parsers.add_parser("triage",
            help="triage a JIRA Bug to:\n" \
                "\tset its Priority to 'Blocker'\n" \
                "\tassign it to the 'Production Bugs' Epic\n" \
                "\tmove it to the current Sprint")
    parser_triage.add_argument("issuekey", help="an existing JIRA issue key")
    parser_triage.add_argument("storypoints", type=int, help="estimated Story Points")
    parser_triage.add_argument("assignee", help="JIRA Assignee")
    parser_triage.set_defaults(func=triage)

    parser_blocker = sub_parsers.add_parser("blocker", help="create a new JIRA Bug and set its Priority to 'Blocker'")
    parser_blocker.add_argument("summary", help="JIRA Issue Summary")
    parser_blocker.set_defaults(func=blocker)

    args = parser.parse_args()

    args.func(args)

def process():
    parse_arguments()


if __name__ == "__main__":
    process()





