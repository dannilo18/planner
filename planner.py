from PyInquirer import prompt
from json import load, loads, dump, dumps
from os import system, chdir, makedirs, path
from pathlib import Path
from datetime import date, datetime


script_path = str(Path().absolute())
active_project_path = script_path + "/projetos"
active_task_path = script_path + "/tasks"
concluded_project_path = script_path + "/projetos_concluidos"
concluded_task_path = script_path + "/tasks_concluidas"

if not path.exists(active_project_path):
    makedirs(active_project_path)

if not path.exists(active_project_path):
    makedirs(active_task_path)

if not path.exists(concluded_project_path):
    makedirs(concluded_project_path)

if not path.exists(concluded_task_path):
    makedirs(concluded_task_path)


def save(planner, concluded):
    if concluded:
        with open("concluded_panner.json", "w", encoding='utf8') as planner_file:
            dump(planner, planner_file, ensure_ascii=False)
    else:
        with open("panner.json", "w", encoding='utf8') as planner_file:
            dump(planner, planner_file, ensure_ascii=False)

def valid_date(project_deadline):
    invalide_date = 1
    while invalide_date:
        deadline = input("Insira o prazo da task (yyyy-mm-dd): ")
        if project_deadline:
            if datetime.strptime(deadline, "%Y-%m-%d") < datetime.today() or datetime.strptime(deadline, "%Y-%m-%d") > datetime.strptime(project_deadline, "%Y-%m-%d"):
                print("Data menor que o dia de hoje ou maior que o limite do projeto. Tente de novo")
            else:
                invalide_date = 0
        else:
            if datetime.strptime(deadline, "%Y-%m-%d") < datetime.today():
                print("Data menor que o dia de hoje. Tente de novo")
            else:
                invalide_date = 0
    
    return deadline


def need_file(project_title, task_title):
    need= "h"
    while need.lower() not in ("y", "n"):
        need = input("Quer escrever um arquivo de resumo? (y/n) ")
        if need.lower() == "y":
            print("Escreva em linha contínua e dê enter ao final.")
            text = input()
            if project_title:
                chdir(active_project_path)
                if task_title:
                    with open("Projeto {} - {}.md".format(project_title, task_title), "w") as text_file:
                        text_file.write(text)
                else:
                    with open("Projeto {}.md".format(project_title), "w") as text_file:
                        text_file.write(text)
            else:
                chdir(active_task_path)
                with open("{}.md".format(task_title), "w") as text_file:
                    text_file.write(text)
    chdir(script_path)
            

try:
    with open("panner.json", "r") as planner_file:
        planner = load(planner_file)
except Exception:
    planner = {
        "tasks": {},
        "projects": {}
    }
    save(planner, 0)

try:
    with open("concluded_planner.json", "r") as planner_file:
        concluded_planner = load(planner_file)
except Exception:
    concluded_planner = {
        "tasks": {},
        "projects": {}
    }
    save(concluded_planner, 1)

def menu_list(name, message, choices):
    question = [
        {
            "type": "list",
            "name": name,
            "message": message,
            "choices": choices,
        }
    ]
    answer = prompt(question)

    return answer[name]


def add(type_selected):
    if type_selected == "Adicionar task isolada;":
        task_title = input("Insira o título da task: ")
        task_deadline = valid_date(None)
        need_file(None,task_title)
        planner["tasks"][task_title] = task_deadline
    elif type_selected == "Adicionar task a projeto;":
        if not planner["projects"]:
            need_project = "h"
            while need_project.lower() not in ("y", "n"):
                need_project = input("Sem projetos cadastrados. Deseja cadastrar um projeto primeiramente? (y/n) ")
            if need_project == "y":
                project = add("Adicionar projeto;")
                task_title = input("Insira o título da task: ")
                task_deadline = valid_date(project[1])
                need_file(project[0],task_title)
                planner["projects"][project][task_title] = task_deadline
            else:
                return "0"
        else:
            answer = menu_list("project", "Selecione o projeto que deseja adicionar task:", planner["projects"].keys())
            task_title = input("Insira o título da task: ")
            task_deadline = valid_date(planner["projects"][answer]["dead_line"])
            need_file(answer, task_title)
            planner["projects"][answer][task_title] = task_deadline
    elif type_selected == "Adicionar projeto;":
        project_title = input("Insira o título do projeto: ")
        project_deadline = valid_date(None)
        need_file(project_title, None)
        planner["projects"][project_title] = {}
        planner["projects"][project_title]["dead_line"] = project_deadline

    save(planner, 0)
    try:
        return project_title, project_deadline
    except Exception:
        return task_title, task_deadline


def show():
    print(dumps(planner, indent=2, ensure_ascii=False))

def main():
    select_1 = menu_list("menu_1", "O que deseja fazer?", ["Adicionar task isolada;", "Adicionar task a projeto;", "Adicionar projeto;",
                                                            "Concluir task isolada;", "Concluir task de projeto;", "Concluir projeto;", "Mostrar planner;", "Sair"])
    if "Adicionar" in select_1:
        add(select_1)
    elif select_1 == "Mostrar planner;":
        show()

if __name__ == "__main__":
    main()
