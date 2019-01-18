import abc
import logging

from google.appengine.api import taskqueue

from stanwood.external_services.gitlab.handlers.mixin import GitlabMixin


class WebhookProjectBase(GitlabMixin):
    @abc.abstractproperty
    def hooks(self):
        return [
            [
                'starts_with_url', {'key': 'value'}
            ]
        ]

    @abc.abstractproperty
    def task_path(self):
        pass

    @abc.abstractmethod
    def hook(*args, **kwargs):
        pass

    def get(self):
        taskqueue.add(
            url=self.task_path,
            queue_name='default'
        )

    def post(self):
        _, projects = self.groups_and_projects(self.stanwood_group)

        for project_group in projects:
            project = self.gitlab.projects.get(project_group.id)
            logging.debug('Checking {} project id'.format(project.id))
            hook_urls = [hook.url for hook in project.hooks.list()]

            for hook_url, kwargs in self.hooks:
                if not any(filter(lambda url: url.startswith(hook_url), hook_urls)):
                    hook = project.hooks.create(dict(url=self.hook(hook_url, project), **kwargs))
                    logging.debug('created {} hook'.format(hook.id))
