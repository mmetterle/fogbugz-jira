from fogbugz import FogBugz
from jira import JIRA
import time

# from datetime import datetime, timedelta
import fbSettings
import jiraSettings

csvfile = ''
flatfile = ''


class JiraImporter:
    def __init__(self):

        self.description = ''
        self.jira = ''
        self.case_prefix = 'FLM-'

        fb = FogBugz(fbSettings.URL, fbSettings.TOKEN)
        self.response = fb.search(  # q="37549,38765,38270,38559,38741",
            # q="opened:1/14/2013",
            # q="Milestone:30.2",
            q='project:"002:FLM" Milestone:"Undecided"',
            # q="38667",
            cols="sCategory,ixBug,nFixForOrder,sTitle,dblStoryPts,sPriority,sStatus,sPersonAssignedTo,"
                 "tags,sFixFor,dtOpened,sProject,plugin_customfields_at_fogcreek_com_qaxbuddyf611,"
                 "ixPersonOpenedBy,plugin_customfields_at_fogcreek_com_salesforcexcaseq17,dtDue,"
                 "plugin_customfields_at_fogcreek_com_hotfixp3b,ixPersonResolvedBy,"
                 "sPersonResolvedBy,hrsCurrEst,dtResolved,dtClosed,sArea,"
                 "ixBugChildren,ixBugParent,events")

        # self.process_fogbugz_data(response)

        # self.write_fields_to_csv_file(jira, response)

    def get_jira_issue(self, issue):

        self.jira = self.reauthenticate()

        return self.jira.issue(issue)

        # jira.add_comment(issue, 'Comment text')

    def reauthenticate(self):

        """ Create a new session and return the session cookie.

        Args:
            username (str): The JIRA username for authentication.
            password (str): The JIRA password for authentication.
            server (str, optional): The URL to the JIRA server. Default value
                is DEFAULT_JIRA_SERVER.
        """
        print("******** reauthenticating jira *********")
        options = {'server': jiraSettings.URL}

        try:
            return JIRA(options, basic_auth=(jiraSettings.USER_NAME, jiraSettings.PASSWORD))
        except Exception as ex:
            errno, strerror = ex.args
            print("error({0}): {1}".format(errno, strerror))

    def process_fogbugz_data(self):
        print("******** processing fogbugz data *********")

        for case in self.response.cases.findAll('case'):
            case_id = self.case_prefix + case.ixBug.string
            events = case.find("events")

            # comments = case.find("events").findAll('dt')

            self.add_event_fields_to_jira(case_id, events)

    def add_event_fields_to_jira(self, case_id, events):
        print("******** adding fields to jira for issue: *********" + "---" + case_id + "------")

        description = ''
        issue = self.get_jira_issue(case_id)

        for event in events:
            try:
                comment = event.s
                event_date = event.dt.string
                event_user = event.sPerson.string
                dateValue = time.strftime('%m/%d/%y %I:%M %p', time.strptime(event_date, '%Y-%m-%dT%H:%M:%SZ'))

                if str(comment.text) != '':
                    if str(description) == '':
                        """ add first comment as description """
                        description = comment.text
                        continue
                    """ add comments """
                    commentStr = dateValue + "; " + event_user + " added: \n \n" + comment.text
                    self.jira.add_comment(issue, commentStr)

                    issue.update(
                        description=description)

            except Exception as ex:
                errno, strerror = ex.args
                print("error({0}): {1}".format(errno, strerror))
                print(" <------ error adding jira data on case: " + case_id + " --------> ")
                print(" <------ Retry on adding fields in jira case_id --------> ")
                continue
