import re
import os
import copy
import sublime
import sublime_plugin

class EmberUberRelatedFilesCommand(sublime_plugin.WindowCommand):

  file_structure_regex_fix = "(?P<app_root>app)(?:/(?P<has_template>templates))?(?(1)/(.*?)/)|/(?P<test>tests)/(?P<test_type>.*?)/(?P<test_dir_ref>.*?)"
  file_structure_regex = "/(?P<app_root>app)(?:/(?P<has_template>templates))?(?(1)/(.*?)/)|/(?P<test>tests)/(?P<test_type>.*?)/(?P<test_dir_ref>.*?)/"
  struct_replacers = {
  "tests": [ "unit", "integration", "acceptance" ],
  "app": [ "templates", "routes", "components", "controllers", "adapters", "helpers", "instance-initializers", "mixins", "models", "serializers", "utils", "services" ],
  "templates": [ "" ]
  }
  file_type_ext = {
    "tests": "-test.js",
    "templates": ".hbs",
    "app": ".js"
  }

  nooop = False

  def run(self):
    self.nooop = False
    def open_related_files(index):
      if index >= 0 and self.nooop == False:
        self.window.open_file(self.file_structure.get("related_files")[index])
    ##

    self.current_view = self.window.active_view()

    self.og_path = self.current_view.file_name()
    self.set_current_file_structure(self.og_path)
    self.set_current_related_files()

    related_files = self.file_structure.get("related_files")

    if related_files == None or len(related_files) == 0:
      related_files = [ 'nooop' ]
      self.nooop = True

    self.window.show_quick_panel(self.file_type_creator(related_files), open_related_files)

  def set_current_file_structure(self, path):
    self.file_structure = {}

    file_structure_search = re.search(self.file_structure_regex, path)

    if file_structure_search is None:
      file_structure_search = re.search(self.file_structure_regex_fix, path)

    path_without_ext, ext = os.path.splitext(path)

    if file_structure_search and len(file_structure_search.groups()) > 0:
      self.file_structure.setdefault("c_app_root", file_structure_search.group('app_root') or file_structure_search.group('test'))
      self.file_structure.setdefault("c_file_type_reference_path", self.path_creator(file_structure_search.groups()))
      self.file_structure.setdefault("c_sub_dir", file_structure_search.group("test_type") or file_structure_search.group(2))
      self.file_structure.setdefault("c_sub_dir_type", file_structure_search.group("test_dir_ref") or file_structure_search.group(3))
      self.file_structure.setdefault("c_ext", ext)
      self.file_structure.setdefault("related_files", [])
      self.file_structure.setdefault("c_path_helper", path_without_ext)

      if self.file_structure.get("c_app_root") == "tests":
        self.file_structure["c_path_helper"] = path_without_ext.replace("-test", '')

  def set_current_related_files(self):
    if self.file_structure.get("c_file_type_reference_path") == None:
      return

    split_path = self.file_structure.get("c_file_type_reference_path").split(os.sep)
    _path = ""
    replaces_shadow = copy.deepcopy(self.struct_replacers)

    if len(split_path) == 3:
      for root_dir, sub_dir in replaces_shadow.items():
        for index in range(len(sub_dir)):
          path_helper = self.file_structure.get("c_path_helper") + self.file_type_ext.get(root_dir)
          if root_dir == "templates":
            # hum that hard coded app tho
            _path = path_helper.replace(self.file_structure.get("c_file_type_reference_path"), "app" + os.sep + root_dir + os.sep + sub_dir[index] + os.sep).replace("//", "/")
            if self.is_valid_path(_path) == False and self.file_structure.get("c_sub_dir_type") is not None:
              _path = path_helper.replace(self.file_structure.get("c_file_type_reference_path"), "app" + os.sep + root_dir + os.sep + self.file_structure.get("c_sub_dir_type") + os.sep).replace("//", "/")

          elif root_dir == "tests" and sub_dir[index] != "acceptance" and self.file_structure.get("c_sub_dir_type") is not None:
              _path = path_helper.replace(self.file_structure.get("c_file_type_reference_path"), root_dir + os.sep + sub_dir[index] + os.sep + self.file_structure.get("c_sub_dir_type") + os.sep)
          else:
            _path = path_helper.replace(self.file_structure.get("c_file_type_reference_path"), root_dir + os.sep + sub_dir[index] + os.sep)

          if self.is_valid_path(_path) and self.og_path != _path:
            self.file_structure.get("related_files").append(_path)

    elif len(split_path) == 4:
      _path_helper = self.file_structure.get("c_path_helper") + self.file_type_ext.get("app")
      if self.file_structure.get("c_sub_dir_type") not in self.struct_replacers.get("app"):
        # since its not in could be routes or controllers
        _path_helper = _path_helper.replace(self.file_structure.get("c_file_type_reference_path"), "app" + os.sep + "routes" + os.sep + self.file_structure.get("c_sub_dir_type") + os.sep)

        if self.is_valid_path(_path_helper) == False:
          _path_helper = _path_helper.replace(self.file_structure.get("c_file_type_reference_path"), "app" + os.sep + "controllers" + os.sep + self.file_structure.get("c_sub_dir_type") + os.sep)
      else:
        _path_helper = _path_helper.replace(self.file_structure.get("c_file_type_reference_path"), "app" + os.sep + self.file_structure.get("c_sub_dir_type") + os.sep)
      if self.is_valid_path(_path_helper):
        self.set_current_file_structure(_path_helper)
        self.set_current_related_files()

  @staticmethod
  def path_creator(regex_res_group):
    path = ""
    for value in regex_res_group:
      if value is not None and value is not '':
        path += value + os.sep
    return path

  @staticmethod
  def file_type_creator(_list_of_files):
    _ref = []
    _x = ""

    for value in _list_of_files:
      res = re.search("(app/(.*?)/.*)", value)
      if res is not None:
        _r = res.groups()
        _x = _r[1].capitalize()[:-1] + ' -> ' + _r[0]

      if "/tests/" in value:
        res = re.search("(tests/(.*?)/.*)", value)
        if res is not None:
          _r = res.groups()
          _x = 'Test: ' + _r[1].capitalize() + ' -> ' + _r[0]
      if _x != "":
        _ref.append(_x)
    return _ref

  @staticmethod
  def is_valid_path(path):
    return os.path.exists(path)

