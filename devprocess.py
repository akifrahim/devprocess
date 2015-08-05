#!/usr/bin/env python
import argparse
import os
from jira import JIRA
import ConfigParser
import keyring
import sys
import json

#TODO: Do all of these
# store password in keyring
# tests (unit/functional)
# logging
# package/install (PyPy)
# refactor (config/init command)

#TODO: Move these defaults to config file
CONFIG_FILE_PATH = os.path.join(os.path.expanduser("~"), ".devconfig")
#JIRA_URL = "http://jira"
#PROJECT_NAME = "Test EOS"
#BOARD_NAME = "Test EOS"
#EPIC_NAME = "Production Bugs"
TRIAGE_PRIORITY_BLOCKER_NAME = "Blocker"
BUG_TYPE_NAME = "Bug"
EPIC_TYPE_NAME = "Epic"
#DEFAULT_ASSIGNEE_NAME = "arahim"


def config(args):
    #store in config file

    print args

    #validate config settings

    print "Validating configuration parameters..."
    try:
        jira = JIRA(args.jira_url, basic_auth=(args.user, args.password))
    except Exception as e:
        if e.status_code == 403:
            print "Invalid username/password. Unable to connect to JIRA. Try again."
            return

        print "Unable to connect to JIRA. Make sure you are on VPN or can get to your JIRA server from this network"
        return

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
    epic_link_field_name = None
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
            epic_link_field_name = field["id"]
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

    epic_issue = jira.search_issues("Project = '{0}' AND issueType = 'Epic' AND 'Epic Name' = '{1}'".format(
        args.projectname, args.epic_name))

    if not epic_issue:
        epic_data = {
            epic_name_field_name: args.epic_name,
            "summary": args.epic_name,
            "issuetype": { "name": EPIC_TYPE_NAME },
            "project": project.key
        }

        #print epic_data

        print 'Could not find an Epic named "{0}". Creating it..."\n'.format(args.epic_name)

        try:
            jira.create_issue(epic_data)
        except:
            print "Failure: Unable to create epic named {0}. Create the epic in project {1} and try again.".format(
                args.epic_name, args.projectname)
            return

        print "Created epic."


    # epic = jira.search_issues('"Epic Name" = "{0}" AND project = "{1}"'.format(args.epic_name, args.projectname))
    # if not epic:
    #     print 'Unable to find epic named "{0}" in project "{1}". Creating it...'.format(args.epic_name, args.projectname)

    #save to file
    config = ConfigParser.RawConfigParser()

    config.add_section("Defaults")
    config.set("Defaults", "user", '"{0}"'.format(args.user))
    config.set("Defaults", "project_name", '"{0}"'.format(args.projectname))
    config.set("Defaults", "board_name", '"{0}"'.format(args.boardname))
    config.set("Defaults", "epic_name", '"{0}"'.format(args.epic_name))

    #store password in keyring
    keyring.set_password("devprocess", args.user, args.password)

    with open(CONFIG_FILE_PATH, "w") as f:
        config.write(f)

    print "Default Configuration set succesfully in {0}".format(CONFIG_FILE_PATH)



def triage(args):
    #print args
    #print "IN TRIAGE"
    #print "Issue Key: {0}".format(args.issuekey)
    # TODO: Move these to config
    # TODO: this should still check for assignee, issuekey and current sprint

    issue_key = args.issuekey
    story_points = args.storypoints
    assignee_name = args.assignee
    
    jira =  JIRA(JIRA_URL, basic_auth=(args.user, args.password))
    issue = jira.issue(issue_key)
    
    #All of this should move to a config file eventually
    #Get field name for Epic Links and assing it to the Epic "Production Bugs"
    #Get Story Points field name and assign points
    #Priority with a value of "Blocker"
    #Assign it to the current Sprint
    
    # priority_field_name = None
    # story_points_field_name = None
    # epic_field_name = None
    # sprint_field_name = None
    # epic = None
    # priority_blocker = None
    #
    # for field in jira.fields():
    #     if field["name"] == "Priority":
    #         priority_field_name = field["id"]
    #     if field["name"] == "Story Points":
    #         story_points_field_name = field["id"]
    #     if field["name"] == "Epic Link":
    #         epic_field_name = field["id"]
    #     if field["name"] == "Sprint":
    #         sprint_field_name = field["id"]
    #
    # for p in jira.priorities():
    #     if p.name == TRIAGE_PRIORITY_BLOCKER_NAME:
    #         priority_blocker = p
    #         break
    #
    # if not priority_blocker:
    #     print 'Could not find a priority named "Blocker". Issue will not be triaged properly\n'
    #
    # epic_issue = jira.search_issues("Project = '{0}' AND issueType = 'Epic' AND 'Epic Name' = '{1}'".format(PROJECT_NAME, EPIC_NAME))
    #
    # if not epic_issue:
    #     print 'Could not find an Epic named "{0}". Issue will not be assigned to this Epic."\n'.format(EPIC_NAME)
    #
    #get the current Sprint - DO NOT move this to a config file as this will change often
    #it should always be found on every invocation
    current_sprint = None
    
    board_id = None
    for board in jira.boards():
        if board.name == BOARD_NAME:
            board_id = board.id
            break
    
    if not board_id:
        print 'Unable to find board "{0}" Will not be able to assign the issue to the active sprint'.format(BOARD_NAME)
    
    sprint_id = None
    for sprint in jira.sprints(board_id, True):
        if sprint.state == "ACTIVE":
            sprint_id = sprint.id
            break

    if not sprint_id:
        print "Could not find an active sprint. Issue will not be assigned to a sprint."

    data = {}
    #Issue with JIRA API that casues a 500 error if fields are already set
    #Only update that fields that are not set correctly
    if getattr(issue.fields(), priority_field_name).id != str(priority_blocker.id):
        data[priority_field_name] = { "id": str(priority_blocker.id) }

    if getattr(issue.fields(), epic_field_name) != epic_issue[0].key:
        data[epic_field_name] = epic_issue[0].key 

    if getattr(issue.fields(), story_points_field_name) != story_points:
        data[story_points_field_name] = story_points
    
    is_sprint_assigned = False
    sprints =  getattr(issue.fields(), sprint_field_name)
    if sprints:
        for sprint in sprints:
            if sprint.split("id=")[-1].strip("]") == str(sprint_id):
                is_sprint_assigned = True
                break
    
    if not is_sprint_assigned:   
    #if getattr(issue.fields(), sprint_field_name)[0].split("id=")[-1].strip("]") != str(sprint_id):
        data[sprint_field_name] = str(sprint_id)
    
    #TODO: Validate that assignee exists as a user in JIRA
    is_assigned = False
    if issue.fields().assignee:
        if issue.fields().assignee.name == assignee_name:
            is_assigned = True
    
    if not is_assigned:
        data["assignee"] = { "name": assignee_name }

#    data = {
#        priority_field_name: { "id": str(priority_blocker.id) },
#        epic_field_name: epic_issue[0].key,
#        #epic_field_name: epic_issue[0].id,
#        story_points_field_name: story_points,
#        sprint_field_name: str(sprint_id),
#        "assignee": { "name": assignee_name } 
#
#    }
    
    #TODO: add a debug log and write the following to it
    #print data

    issue.update(fields=data)

    print "Issue {0} Triaged successfully".format(issue.key)


def blocker(args):
    #print args
    summary = args.summary

    jira =  JIRA(JIRA_URL, basic_auth=(args.user, args.password))

    project_key = next((p.key for p in jira.projects() if p.name == PROJECT_NAME), None)

    if not project_key:
        print "Unable to find project {0}. Failed to create a new issue."
        return

    data = {
        "project": project_key,
        "issuetype": { "name": BUG_TYPE_NAME },
        "priority": { "name": TRIAGE_PRIORITY_BLOCKER_NAME },
        "assignee": { "name": DEFAULT_ASSIGNEE_NAME },
        "summary": summary

    }

    issue = jira.create_issue(data)

    print 'Bug {0} created and assigned a priority of "Blocker"\n' \
            'This needs to be triaged immediately. For help with triage enter: \n' \
            './devprocess triage --help'.format(issue.key)
    

def parse_arguments():
    #parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    #parser.add_argument('--user', action="store")
    #parser.add_argument('--password', action="store")
    #parser.add_argument("command", choices=["triage", "create"])
    #help="triage a Bug as a Blocker in JIRA")
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


    #parser_triage = sub_parsers.add_parser("triage", formatter_class=argparse.RawTextHelpFormatter,
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
    #print args 
    args.func(args)

def process():
    parse_arguments()
    #check if config exists. if it doesn't then "init" it
    #create a new command calle dinit to define a new config file and
    #get all the field names required



if __name__ == "__main__":
    process()





