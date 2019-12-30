"""Create a new project.

Functions:
    make_project - Use this to create a project.

Classes:
    EProjectTemplates - Available project templates.


Format Arguments - Argument instances (surrounded in braces {}) are
replaced with their values when creating a project.
Available arguments:
    {display_name} - Chosen display name of project.
    {project_name} - Chosen internal name of project.
        Variants: {ProjectName} - Pascal case conversion.
    {project_dir} - Root directory of project.
    {project_desc} - Short description of project.
    {copyright_notice} - Copyright notice of project.
"""

import os
from factorygame.utils.fmt import to_pascal, to_snake


class EProjectTemplates:
    """Available project templates to choose from.
    """

    EMPTY = 0
    # PUZZLE = 1
    # ADVENTURE = 2
    # ANIMATION = 3

    MAX = 1


class _ProjectTemplate:
    """Set values for a project template.
    """

    def __init__(self, **kw):
        """Declare a project template.
        """

        self.formatted_name = ""
        self.formatted_description = ""
        self.formatted_long_description = ""

        self.name = kw.get("name", "template_name")
        self.description = kw.get("description", "")
        self.long_description = kw.get("long_description", "")

        self.files = kw.get("files", [])

    def format_template(self, format_args):
        """Format the contents of the project template.
        """

        self.formatted_name = self.name.format(**format_args)
        self.formatted_description = self.description.format(**format_args)
        self.formatted_long_description = (
            self.long_description.format(**format_args))

        for file in self.files:
            file.format_template(format_args)


class _FileTemplate:
    """Set default values for a template and create the file.
    """

    def __init__(self, filename, contents):
        """Declare file template.
        """
        self.formatted_filename = ""
        self.formatted_contents = ""

        if isinstance(filename, str):
            # Filename given as single string argument.
            self.filename = filename
        else:
            # Filename given as list of multiple folders.
            # Use OS specific directory name if nested directory given.
            self.filename = os.path.join(*filename)

        if isinstance(contents, str):
            # Contents were given as single string argument.
            self.contents = contents
        else:
            # Contents given as list of multiple lines.
            # Combine into one string separated by newline character.
            self.contents = "\n".join(contents)

    def format_template(self, format_args):
        """Format the contents of the file and filename.
        """
        self.formatted_filename = self.filename.format(**format_args)
        self.formatted_contents = self.contents.format(**format_args)

    def write_to_disk(self, root_directory=""):
        """Format and write contents to disk.

        Assumes root_directory exists.
        """

        disk_filename = os.path.join(root_directory, self.formatted_filename)
        with open(disk_filename, "w") as fp:
            fp.write(self.formatted_contents)


_PROJECT_TEMPLATES = {}

_PROJECT_TEMPLATES[EProjectTemplates.MAX] = _ProjectTemplate(
    name="Invalid Project Template")

_PROJECT_TEMPLATES[EProjectTemplates.EMPTY] = _ProjectTemplate(
    name="Empty Launchable Project",
    description="Minimum files for a launchable project.",
    files=[
        _FileTemplate(
            "main.py", (

            '"""Default project start for {project_name}.',
            '',
            '{copyright_notice}',
            '"""',
            '',
            'from factorygame import GameplayUtilities',
            'from {project_name} import {ProjectName}Engine',
            '',
            'if __name__ == "__main__":',
            '   # Create the game.',
            '   GameplayUtilities.create_game_engine({ProjectName}Engine)')
            ),

        _FileTemplate((
            "{project_name}",
                "__init__.py"), (

            '"""{project_desc}',
            '',
            '{copyright_notice}',
            '',
            '"""',
            '',
            'from {project_name}.{project_name}_engine '
            'import {ProjectName}Engine',
            '')
            ),

        _FileTemplate((
            "{project_name}",
                "{project_name}_engine.py"), (

            '"""Game engine class for {display_name}.\n',
            '"""',
            '',
            'from factorygame import GameEngine',
            'from factorygame.core.input_base import EKeys'
            '',
            'class {ProjectName}Engine(GameEngine):',
            '   """',
            '   """',
            '',
            '   def __init__(self):',
            '       """Set default values.',
            '       """',
            '',
            '       super().__init__()',
            '       self._frame_rate = 60',
            '       self._window_title = "{display_name}"',
            '       # self._starting_world = WorldGraph',
            '',
            '   def setup_input_mappings(self):',
            '       """Declare any input mappings.',
            '       """',
            '',
            '       # self.input_mappings.add_action_mapping('
            '"MappingName", EKeys.M)',
            '')
            )
        ])


def make_project(root_dir, name, template=None):
    """Create project folder for a new project.

    This will create a new folder in the root called the project name
    which will contain the project.
    """

    if template is None:
        template = EProjectTemplates.EMPTY

    # Format arguments will be templated in templates.
    format_args = {
        "project_dir": os.path.join(root_dir, name),
        "display_name": name,
        "project_name": to_snake(name),
        "ProjectName": to_pascal(name),
        "project_desc": "",
        "copyright_notice": ("Fill out your copyright notice in the "
                             "Description page of Project Settings.")}

    # All projects need minimum files.
    basic_template_data = _PROJECT_TEMPLATES[EProjectTemplates.EMPTY]
    basic_template_data.format_template(format_args)
    _create_template_files(basic_template_data, format_args["project_dir"])

    if template != EProjectTemplates.EMPTY:
        # Create additional project files for chosen template.
        template_data = _PROJECT_TEMPLATES[template]
        template_data.format_template(format_args)
        _create_template_files(template_data, format_args["project_dir"])

def _create_template_files(project_template, project_dir):
    """Create files on disk following template.

    Assumes files are already formatted.
    :see: method _ProjectTemplate.format_template
    """

    # Create project root folder already exists.
    try:
        _make_dir(project_dir)
    except FileExistsError as e:
        raise FileExistsError("Cannot create project when folder '%s' "
                              "already exists" % project_dir) from e
    except IOError as e:
        raise IOError("Failed to create project") from e

    # Create each template file.
    for template_file in project_template.files:
        abs_filename = os.path.join(
            project_dir, template_file.formatted_filename)
        file_path, _ = os.path.split(abs_filename)
        if not os.path.exists(file_path):
            # Make directory ready for file to be written.
            _make_dir(file_path)

        template_file.write_to_disk(project_dir)

def _make_dir(directory_name):
    """Create a directory, with support for nested directories.

    :param directory_name: (str) New directory/directories to make.
    Must lead to a folder, not a filename.

    Raise FileExistsError if the directory already exists.
    Raise IOError if couldn't be made for any other reason.
    """

    # Check if project root folder already exists.
    if os.path.exists(directory_name):
        raise FileExistsError("Folder '%s' already exists" % directory_name)

    # Create project folder.
    try:
        os.makedirs(directory_name)
    except OSError:
        if os.path.exists(directory_name):
            raise FileExistsError("Folder '%s' already exists"
                % directory_name)
        else:
            raise IOError("Failed to create folder '%s'" % directory_name)
