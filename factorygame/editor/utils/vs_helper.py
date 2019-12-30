"""Create Visual Studio solution for FactoryGame projects.

This will let an active FactoryGame game be opened in Visual Studio
IDE and be edited. It will detect the modules within the project
folder and add them to the solution.

Detecting files relies on any module or submodule of the module
of the same name as the project name but with all small letters
and spaces separated with underscores. "My Project" -> "my_project"
"""

import argparse
import uuid
import os


_TEMPLATE_SLN = ('ï»¿\n'
 'Microsoft Visual Studio Solution File, Format Version 12.00\n'
 '# Visual Studio Version 16\n'
 'VisualStudioVersion = 16.0.29509.3\n'
 'MinimumVisualStudioVersion = 10.0.40219.1\n'
 'Project("{{{language_guid}}}") = "{project_name}", "{project_name}.pyproj", '
 '"{{{project_guid}}}"\n'
 'EndProject\n'
 'Global\n'
 '\tGlobalSection(SolutionConfigurationPlatforms) = preSolution\n'
 '\t\tDebug|Any CPU = Debug|Any CPU\n'
 '\t\tRelease|Any CPU = Release|Any CPU\n'
 '\tEndGlobalSection\n'
 '\tGlobalSection(ProjectConfigurationPlatforms) = postSolution\n'
 '\t\t{{{project_guid}}}.Debug|Any CPU.ActiveCfg = Debug|Any CPU\n'
 '\t\t{{{project_guid}}}.Release|Any CPU.ActiveCfg = Release|Any CPU\n'
 '\tEndGlobalSection\n'
 '\tGlobalSection(SolutionProperties) = preSolution\n'
 '\t\tHideSolutionNode = FALSE\n'
 '\tEndGlobalSection\n'
 '\tGlobalSection(ExtensibilityGlobals) = postSolution\n'
 '\t\tSolutionGuid = {{{solution_guid}}}\n'
 '\tEndGlobalSection\n'
 'EndGlobal\n')

_TEMPLATE_PYPROJ = ('<Project DefaultTargets="Build" '
 'xmlns="http://schemas.microsoft.com/developer/msbuild/2003" '
 'ToolsVersion="4.0">\n'
 '  <PropertyGroup>\n'
 '    <Configuration Condition=" \'$(Configuration)\' == \'\' '
 '">Debug</Configuration>\n'
 '    <SchemaVersion>2.0</SchemaVersion>\n'
 '    <ProjectGuid>{project_guid}</ProjectGuid>\n'
 '    <ProjectHome>.</ProjectHome>\n'
 '    <StartupFile>main.py</StartupFile>\n'
 '    <SearchPath>\n'
 '    </SearchPath>\n'
 '    <WorkingDirectory>.</WorkingDirectory>\n'
 '    <OutputPath>.</OutputPath>\n'
 '    <Name>{project_name}</Name>\n'
 '    <RootNamespace>{project_name}</RootNamespace>\n'
 '  </PropertyGroup>\n'
 '  <PropertyGroup Condition=" \'$(Configuration)\' == \'Debug\' ">\n'
 '    <DebugSymbols>true</DebugSymbols>\n'
 '    <EnableUnmanagedDebugging>false</EnableUnmanagedDebugging>\n'
 '  </PropertyGroup>\n'
 '  <PropertyGroup Condition=" \'$(Configuration)\' == \'Release\' ">\n'
 '    <DebugSymbols>true</DebugSymbols>\n'
 '    <EnableUnmanagedDebugging>false</EnableUnmanagedDebugging>\n'
 '  </PropertyGroup>\n'
 '{included_files}\n'
 '{included_folders}\n'
 '  <Import '
 'Project="$(MSBuildExtensionsPath32)\\Microsoft\\VisualStudio\\v$(VisualStudioVersion)\\Python '
 'Tools\\Microsoft.PythonTools.targets" />\n'
 '  <!-- Uncomment the CoreCompile target to enable the Build command in\n'
 '       Visual Studio and specify your pre- and post-build commands in\n'
 '       the BeforeBuild and AfterBuild targets below. -->\n'
 '  <!--<Target Name="CoreCompile" />-->\n'
 '  <Target Name="BeforeBuild">\n'
 '  </Target>\n'
 '  <Target Name="AfterBuild">\n'
 '  </Target>\n'
 '</Project>')


class VsProjectHelper:
    """Generate files for FactoryGame projects for use Visual Studio.

    Usage:
    `VsProjectHelper.generate_solution("c:/myproject", "MyProject")`
    """

    ## Python projects in Visual Studio are identified by this GUID.
    PYTHON_GUID = "888888A0-9F3D-457C-B088-3A5042F75D52"

    ## Name of files containing boilerplate code to be formatted.
    TEMPLATE_FILENAME_PREFIX = "generate_visual_studio_project_example"

    @staticmethod
    def generate_solution(directory, project_name, **kw):
        """Create the solution files in the set directory.

        :param directory: (str) Root of project where .sln will be made.

        :param project_name: (str) Format name of project.

        :keyword project_guid: (str) Visual studio project GUID.
        Randomly generated if omitted.

        :keyword solution_guid: (str) Visual studio solution GUID.
        Randomly generated if omitted.

        :return: (bool) Whether it was created successfully.
        """

        # Read templates from disk.
        #template_sln, template_pyproj = VsProjectHelper._read_templates()
        template_sln, template_pyproj = _TEMPLATE_SLN, _TEMPLATE_PYPROJ

        # Insert formatted values in memory.
        format_args = VsProjectHelper._get_format_args(
            directory, project_name, **kw)
        formatted_sln = template_sln.format(**format_args)
        formatted_pyproj = template_pyproj.format(**format_args)

        # Write back to disk.
        VsProjectHelper._write_formatted(
            formatted_sln, formatted_pyproj, format_args)

    @staticmethod
    def _set_directory_items(format_args):
        """Add arguments for files and folders in directory.
        """

        ITEM_GROUP = (
            "  <ItemGroup>\n"
            "{items}\n"
            "  </ItemGroup>")

        FILE_ITEM = (
            '    <Compile Include="{filename}">\n'
            '      <SubType>Code</SubType>\n'
            '    </Compile>')

        FOLDER_ITEM = (
            '    <Folder Include="{dirname}\\" />')

        # Find module with snake case version of project name.
        project_module = format_args["project_name"].lower().replace(" ", "_")
        abs_module_root = os.path.join(
            format_args["project_root"], project_module)

        file_items = []
        folder_items = []
        if os.path.exists(abs_module_root):
            folder_items.append(FOLDER_ITEM.format(dirname=project_module))

        # Only look in the project module named in snake case.
        for root, dirs, files in os.walk(abs_module_root):
            if root.endswith("__pycache__"):
                # Don't add pycache folders and files to the project.
                continue

            # Remove full system path.
            root = os.path.relpath(root, format_args["project_root"])
            file_items += [
                FILE_ITEM.format(filename=os.path.join(root, file))
                for file in files]

            folder_items += [
                FOLDER_ITEM.format(dirname=os.path.join(root, dirname))
                for dirname in dirs
                if dirname != "__pycache__"]  # Ignore pycache in this folder.

        # Add starting file.
        file_items.append('    <Compile Include="main.py" />')

        format_args["included_files"] = ITEM_GROUP.format(
            items="\n".join(file_items))
        format_args["included_folders"] = ITEM_GROUP.format(
            items="\n".join(folder_items))

    @staticmethod
    def _set_guids(format_args):
        """Add arguments for any GUIDs that are not specified yet.
        """

        format_args["language_guid"] = VsProjectHelper.PYTHON_GUID

        # Generate random GUIDs if omitted or None.
        # Command line arguments may have assigned None values.
        if format_args["project_guid"] is None:
            format_args["project_guid"] = str(uuid.uuid4()).upper()
        if format_args["solution_guid"] is None:
            format_args["solution_guid"] = str(uuid.uuid4()).upper()

    @staticmethod
    def _get_format_args(directory, project_name, **kw):
        """Return dictionary of values to format template files.
        """

        format_args = {
            "project_root": directory,
            "project_name": project_name,
            "project_guid": kw.get("project_guid"),
            "solution_guid": kw.get("solution_guid"),
            "included_files": None,
            "included_folders": None
            }

        VsProjectHelper._set_directory_items(format_args)
        VsProjectHelper._set_guids(format_args)

        return format_args

    @staticmethod
    def read_templates():
        """Return contents of template .sln and .pyproj files.
        """

        # Open the example files.
        sln_filename = TEMPLATE_FILENAME_PREFIX + ".sln"
        with open(sln_filename) as fp:
            original_sln = fp.read()

        pyproj_filename = TEMPLATE_FILENAME_PREFIX + ".pyproj"
        with open(pyproj_filename) as fp:
            original_pyproj = fp.read()

        return original_sln, original_pyproj

    @staticmethod
    def _write_formatted(sln_contents, pyproj_contents, format_args):
        """Write or overwrite files containing provided contents.
        """

        # Write into new files in one directory up.
        sln_filename = "{project_root}/{project_name}.sln".format(
            **format_args)
        with open(sln_filename, "w") as fp:
            fp.write(sln_contents)

        pyproj_filename = "{project_root}/{project_name}.pyproj".format(
            **format_args)
        with open(pyproj_filename, "w") as fp:
            fp.write(pyproj_contents)

def _parse_args():
    """Declare and parse command line arguments.

    :return: (dict) Parsed command line arguments.
    """

    parser = argparse.ArgumentParser(
        description="Create Visual Studio solution for FactoryGame "
            "projects.")

    parser.add_argument(
        "project_root",
        help="Project directory to search for module and to place"
            "solution in.")

    parser.add_argument(
        "project_name",
        help="Name of project for naming the solution")

    parser.add_argument(
        "--project-guid",
        help="Visual studio project GUID. Randomly generated if omitted.")

    parser.add_argument(
        "--solution-guid",
        help="Visual studio solution GUID. Randomly generated if omitted.")

    # Load command line arguments.
    parsed_args = parser.parse_args()
    return parsed_args

def main():
    # Create solution from command line arguments.
    parsed_args = _parse_args()

    VsProjectHelper.generate_solution(
        directory=parsed_args.project_root,
        project_name=parsed_args.project_name,
        project_guid=parsed_args.project_guid,
        solution_guid=parsed_args.solution_guid)

if __name__ == '__main__':
    main()

