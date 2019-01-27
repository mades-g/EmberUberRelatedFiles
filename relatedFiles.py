import re
import os
import copy
import sublime
import sublime_plugin

default_root = {
  'app': '.js',
  'tests': '-test.js'
}

default_files_config = {
  'tests': default_root['tests'],
  'templates': '.hbs'
}

class EmberUberRelatedFilesCommand(sublime_plugin.WindowCommand):
  def run(self):
    self.current_view = self.window.active_view()
    self.og_path = self.current_view.file_name()

    file_config = self.create_types_config()

    self.find_related(**file_config)

  def get_project_type(self, path):
    project_root = 'app'

    if default_files_config['tests'] in path:
      project_root = 'tests'
    elif default_files_config['templates'] in path:
      project_root = 'templates'

    return project_root

  # return {Dict}
  def create_types_config(self):

    reg = ''
    file_config = {}
    path = self.og_path
    is_root_path = False
    project_type = self.get_project_type(path)
    self.project_root = re.sub('(.*{root}{sep}).*'.format_map({'sep': os.sep, 'root': project_type}), r'\1', path)

    ext = default_files_config.get(project_type, '.js')
    reg = '{project_root}(.*)(?={ext})'.format_map({'project_root': self.project_root, 'ext': ext})

    sub_paths_info_res = re.search(reg, path)

    if sub_paths_info_res is not None:
      file_id = sub_paths_info_res.groups()[0].split(os.sep)[0]
      file_config['name'] = sub_paths_info_res.groups()[0].split(os.sep)[-1]
      sub_paths_len = len(sub_paths_info_res.groups()[0].split(os.sep))

      if file_id == 'acceptance':
        # messy one
        file_config['section_type'] = 'routes'
        file_path_res = re.search('.*{sep}{type}{sep}(.*){sep}{name}'.format_map({'sep': os.sep, 'type': file_id, 'name': file_config['name']}), path)

        if file_path_res is not None:
          file_config['path'] = file_path_res.group(1)
      else:
        file_config['section_type'] = sub_paths_info_res.groups()[0].split(os.sep)[0]

      file_path_res = re.search('.*{sep}{type}{sep}(.*){sep}{name}'.format_map({'sep': os.sep, 'type': file_config['section_type'], 'name': file_config['name']}), path)

      if file_path_res is not None:
          file_config['path'] = file_path_res.group(1)

      if project_type == 'templates':
        file_config['type'] = 'app'
      else:
        file_config['type'] = project_type
      file_config.setdefault('path', os.sep)

    return  file_config

  def find_related(self, **file_config):
    related = []
    path = file_config['path']
    section_type = file_config['section_type']
    file_name = file_config['name']

    for root in default_root:
      project_root = re.sub('(.*{root}{os_sep}).*'.format_map({'os_sep': os.sep, 'root': file_config['type']}), r'\1', self.og_path)

    return related