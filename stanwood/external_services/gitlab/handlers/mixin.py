import abc

import gitlab


class GitlabMixin(object):

    @abc.abstractproperty
    def gitlab(self):
        pass

    @staticmethod
    def _gitlab(host, private_token, per_page=50):
        return gitlab.Gitlab(host, private_token=private_token, per_page=per_page)

    @staticmethod
    def _gitlab_user(host, gitlab_access_token):
        return gitlab.Gitlab(host, oauth_token=gitlab_access_token)

    @property
    def stanwood_group(self):
        return self.gitlab.groups.get('stanwood')

    def groups_and_projects(self, group):
        groups, projects = [group], group.projects.list()

        for subgroup in group.subgroups.list():
            subbed = self.gitlab.groups.get(subgroup.id)
            sub_groups, sub_projects = self.groups_and_projects(subbed)

            groups.extend(sub_groups)
            projects.extend(sub_projects)

        return groups, projects
