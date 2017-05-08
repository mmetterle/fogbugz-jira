from fogbugz import FogBugz
from jira import JIRA, JIRAError
import time
import os

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
        self.response = fb.search(#q='project:"002:FLM" Milestone:"31.1"',
                                  # q="38741",
                                  q="38923,39122,39123,39124",
                                   cols="sCategory,ixBug,nFixForOrder,sTitle,dblStoryPts,sPriority,sStatus,sPersonAssignedTo,"
                                       "tags,sFixFor,dtOpened,sProject,plugin_customfields_at_fogcreek_com_qaxbuddyf611,"
                                       "ixPersonOpenedBy,plugin_customfields_at_fogcreek_com_salesforcexcaseq17,dtDue,"
                                       "plugin_customfields_at_fogcreek_com_hotfixp3b,ixPersonResolvedBy,"
                                       "sPersonResolvedBy,hrsCurrEst,dtResolved,dtClosed,sArea,"
                                       "ixBugChildren,ixBugParent,events")

        #self.process_fogbugz_data(self.response)

        # q="37549,38765,38270,38559,38741",
        # q="opened:1/14/2013",
        # q='project:"002:FLM" Milestone:"Undecided"',
        # q="38667",
        # self.write_fields_to_csv_file(jira, response)

    def get_jira_issue(self, issue_id):

        try:
            self.jira = self.reauthenticate()
            return self.jira.issue(issue_id)

        except JIRAError as e:
            print("issue id: {}".format(issue_id))
            print(e.status_code, e.text)
            return None

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

    def create_versions(self):
        self.jira = self.reauthenticate()
        self.milestone_list = self.read_milestone_data()

        for milestone in self.milestone_list:
            print("******** adding milestone ********* \n")
            print("********" + milestone + "*********")
            self.jira.create_version(milestone, "ML")

    def read_milestone_data(self):
        print("******** reading flat file *********")

        global flatfile
        current_path = os.getcwd()
        flat_file = current_path + "\\utilities\\milestone_list.txt"
        print(flat_file)

        try:
            lines = []
            with open(flat_file, 'r') as flatfile:
                for line in flatfile:
                    line = line.strip()  # or someother preprocessing
                    lines.append(line)

        except IOError as err:
            errno, strerror = err.args
            print("I/O error({0}): {1}".format(errno, strerror))
        # finally:
        #    flat_file.close()

        # for keys, values in user_dict.items():
        #   print(keys)
        #    print(values)

        return lines

    def process_fogbugz_data(self):
        print("******** processing fogbugz data *********")

        for case in self.response.cases.findAll('case'):
            case_id = self.case_prefix + case.ixBug.string
            events = case.find("events")

            # comments = case.find("events").findAll('dt')
            issue = self.get_jira_issue(case_id)
            if issue is not None:
                print("****** receiving None *******")
                self.add_event_fields_to_jira(case_id, issue, events)

    # def read_retry_data(self):
    #    print("******** reading flat file *********")
    #
    #    global flatfile
    #    current_path = os.getcwd()
    #    flat_file = current_path + "\\retry_again_file.txt"
    #
    #    try:
    #        user_dict = {}
    #        with open(flat_file, 'r') as flatfile:
    #            for line in flatfile:
    #                split_line = line.split()
    #                self.call_fogbugz(split_line[0])
    #                # print(self.case_prefix + split_line[0])
    #
    #                # user_dict[int(split_line[0])] = " ".join(split_line[1:])
    #
    #    except IOError as err:
    #        errno, strerror = err.args
    #        print("I/O error({0}): {1}".format(errno, strerror))
    #    # finally:
    #    #    flat_file.close()
    #
    #        # for keys, values in user_dict.items():
    #    #   print(keys)
    #    #    print(values)
    #
    #    return user_dict

    # def call_fogbugz(self, case_id):
    #    fb = FogBugz(fbSettings.URL, fbSettings.TOKEN)
    #    self.response = fb.search(q=case_id, cols="events")
    #    # print("FB call successful")
    #    events = self.response.cases.find("events")
    #    self.add_event_fields_to_jira(case_id, events)

    def add_event_fields_to_jira(self, case_id, issue, events):
        print("******** adding fields to jira for issue: *********" + "---" + case_id + "------")

        descriptionstr = ''
        # issue_id = self.case_prefix + case_id
        #issue = self.get_jira_issue(case_id)

        for event in events:
            try:
                comment = event.s
                event_date = event.dt.string
                event_user = event.sPerson.string
                dateValue = time.strftime('%m/%d/%y %I:%M %p', time.strptime(event_date, '%Y-%m-%dT%H:%M:%SZ'))

                if str(comment.text) != '':
                    if str(descriptionstr) == '':
                        """ add first comment as description """
                        descriptionstr = comment.text
                        issue.update(
                            description=descriptionstr)
                        continue
                    """ add comments """
                    commentStr = dateValue + "; " + event_user + " added: \n \n" + comment.text
                    self.jira.add_comment(issue, commentStr)

            except Exception as ex:
                errno, strerror = ex.args
                print("error({0}): {1}".format(errno, strerror))
                print("<------ error adding jira data on case: " + case_id + " -------->")
                print("<------ Retry on adding fields in jira case_id -------->")
                continue