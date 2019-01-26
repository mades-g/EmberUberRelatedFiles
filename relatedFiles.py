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
  'templates': '.hbs',
  'app': default_root['app']
}

class EmberUberRelatedFilesCommand(sublime_plugin.WindowCommand):
  def run(self):
    self.current_view = self.window.active_view()
    self.og_path = self.current_view.file_name()

    file_config = self.create_types_config(self.og_path)

    related_files = self.find_related(**file_config)

  # return {Dict}
  def create_types_config(self, path):
    file_config = {}
    is_root_path = False
    # Order regarding `tests` and `project type` matters
    reg = ''
    for file_type in default_files_config:
      ext = default_files_config[file_type]
      if ext in path:
        if file_type == 'tests':
          file_config['type'] = file_type
          reg = '{type_config}{os_sep}\\w+{os_sep}(?P<section_type>\\w+){os_sep}(.*{os_sep})(?=(?P<file_name>.*){ext})'.format_map({'type_config': file_type, 'os_sep': os.sep, 'ext': ext})
          break;

        file_config['type'] = 'app'

    search_res = re.search(reg, path)

    if search_res is not None:
      file_config['path'] = '/' if is_root_path else search_res.groups()[1]
      file_config['section_type'] = search_res.group('section_type')
      file_config['name'] = search_res.group('file_name')

    return file_config

  def find_related(self, **file_config):
    related = []
    path = file_config['path']
    section_type = file_config['section_type']
    file_name = file_config['name']
    project_root = re.sub('(.*{root}{os_sep}).*'.format_map({'os_sep': os.sep, 'root': file_config['type']}), r'\1', self.og_path)

    for root in default_root:
      project_root = re.sub('(\\w+){os_sep}$'.format_map({'os_sep': os.sep}), root + os.sep, project_root)

      for root_path, dirs, files in os.walk(project_root):

        for dir in dirs:
          if dir != 'acceptance' and root == 'tests':
            lookup = project_root + dir + os.sep + section_type + os.sep + path
          else:
            lookup = project_root + dir + os.sep + path
          if os.path.exists(lookup):
            if 'templates' in lookup:
              found = lookup + file_name + default_files_config['templates']
            else:
              found = lookup + file_name + default_root[root]

            if os.path.isfile(found) and found != self.og_path and found not in related:
              related.append(found)

    return related