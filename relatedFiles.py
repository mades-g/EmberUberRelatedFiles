import re
import os
import copy
import sublime
import sublime_plugin

class EmberUberRelatedFilesCommand(sublime_plugin.WindowCommand):

  file_structure_regex = "/(?P<app_root>app)(?:/(?P<has_template>templates))?(?(1)/(.*?)/)|/(?P<test>tests)/(?P<test_type>.*?)/(?P<test_dir_ref>.*?)/"
  struct_replacers = {
  "tests": [ "unit", "integration", "acceptance" ],
  "app": [ "templates", "adapters", "helpers", "instance-initializers", "mixins", "models", "serializers", "utils", "routes", "components", "controllers" ],
  "templates": [ "routes" , "components"]
  }
  file_type_ext = {
    "tests": "-test.js",
    "templates": ".hbs",
    "app": ".js"
  }

  def run(self):
    pass

  def set_current_file_structure(self, path):
    self.og_path = path
    self.file_structure = {}

    file_structure_search = re.search(self.file_structure_regex, path)
    path_without_ext, ext = os.path.splitext(path)

    if len(file_structure_search.groups()) > 0:
      self.file_structure.setdefault("c_app_root", file_structure_search.group('app_root') or file_structure_search.group('test'))
      self.file_structure.setdefault("c_file_type_reference_path", self.path_creator(file_structure_search.groups()))
      self.file_structure.setdefault("c_type", file_structure_search.group("test_type") or file_structure_search.group(3))
      self.file_structure.setdefault("c_path_helper", re.sub(self.file_structure.get("c_file_type_reference_path"), "app_root" + os.sep + "sub_dir" + os.sep + "sub_dir_type" + os.sep, path_without_ext))
      self.file_structure.setdefault("c_ext", ext)
      self.file_structure.setdefault("related_files", [])

  def set_current_related_files(self):
    pass

  @staticmethod
  def path_creator(regex_res_group):
    path = ""
    for value in regex_res_group:
      if value is not None and value is not '':
        path += value + os.sep
    return path

  @staticmethod
  def is_valid_path(path):
    return os.path.exists(path)

