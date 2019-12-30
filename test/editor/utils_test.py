from factorygame.editor.utils.project import make_project, EProjectTemplates

root_dir = "projects"
project_name = "MyProject"
template = EProjectTemplates.EMPTY
make_project(root_dir, project_name, template)
