from PyInquirer import prompt
from os import system, chdir, makedirs, path
from datetime import date, datetime, timedelta
from json import dump, dumps, load, loads


def init(script_path):
    #data structure
    structures = ["/dates_planner.json", "/tasks_planner.json", "/projects_planner.json"]
    for structure in structures:
        if not path.isfile(script_path + structure):
            if "dates" in structure:
                planner = {}
                today = datetime.today().date()
                end = today + timedelta(days=365 * 3)
                delta = end - today
                for i in range(delta.days+1):
                    planner[(today + timedelta(days=i)
                             ).strftime("%Y-%m-%d")] = []
            elif "projects" in structure:
                planner = {
                    "Avulso": {
                        "deadline": "2030-01-01",
                        "tasks": [],
                        "done": True
                    }
                }
            else:
                planner = {}
            with open(structure.replace("/", ""), "w") as structure_file:
                dump(planner, structure_file)


def return_available(planner, flag):
    available = []
    if flag:
        for key in planner:
            if not planner[key]["done"]:
                available.append({
                    "name": key
                })
        available.append({
            "name": "Voltar"
        })
    else:
        for key in planner:
            if not key["done"]:
                available.append(key)
    
    return available

def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]


def save(planner, name):
    with open("{}.json".format(name[0]), "w", encoding='utf8') as planner_file:
        dump(planner, planner_file, ensure_ascii=False)


def valid_date(project_deadline):
    invalide_date = 1
    while invalide_date:
        deadline_str = input("Insira o prazo da task (yyyy-mm-dd): ")   
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
        if project_deadline:
            if deadline < datetime.today() or deadline > datetime.strptime(project_deadline, "%Y-%m-%d"):
                print(
                    "Data menor que o dia de hoje ou maior que o limite do projeto/task. Tente de novo")
            else:
                invalide_date = 0
        else:
            if deadline < datetime.today():
                print("Data menor que o dia de hoje. Tente de novo")
            else:
                invalide_date = 0

    return deadline_str


def menu_list(inputs):
    questions = []
    for question in inputs:
        questions.append({
            "type": "list",
            "name": question["name"],
            "message": question["message"],
            "choices": question["choices"],
        })
    answers = prompt(questions)

    return answers

def add(main):
    with open("projects_planner.json", "r") as project_file:
        projects_planner = load(project_file)
    with open("tasks_planner.json", "r") as tasks_file:
        tasks_planner = load(tasks_file)
    with open("dates_planner.json", "r") as dates_file:
        dates_planner = load(dates_file)
    if main == "Tasks":
        questions = [
            {
                "name": "classification",
                "message": "Qual a classificação:",
                "choices": ["Trabalho", "Pessoal", "Financeiro"]
            },
            {
                "name": "project",
                "message": "Selecione a qual projeto essa task faz parte:",
                "choices": list(projects_planner.keys()) + ["Voltar"]
            }
        ]
        task = menu_list(questions)
        if task["project"] == "Voltar":
            secondary_menu(main)
            return
        task["name"] = input("Qual o título da task? ")
        task["deadline"] = valid_date(projects_planner[task["project"]]["deadline"])
        task["resume"] = input("Resumo da task: ")
        task["done"] = False
        task["delta_time"] = None
        task["finish_date"] = None
        if task["project"] != "Avulso":
            if task["classification"] != projects_planner[task["project"]]["classification"]:
                task["classification"] = projects_planner[task["project"]]["classification"]
        tasks_planner[task["name"]] = task
        projects_planner[task["project"]]["tasks"].append(task)
        dates_planner[task["deadline"]].append(task)

    elif main == "Projetos":
        questions = [
            {
                "name": "classification",
                "message": "Qual a classificação:",
                "choices": ["Trabalho", "Pessoal", "Financeiro", "Voltar"]
            }
        ]
        project = menu_list(questions)
        if project["classification"] == "Voltar":
            secondary_menu(main)
            return
        project["name"] = input("Qual o título da projeto? ")
        project["deadline"] = valid_date("2030-12-31")
        project["resume"] = input("Resumo do projeto: ")
        project["done"] = False
        project["delta_time"] = None
        project["finish_date"] = None
        project["tasks"] = []
        projects_planner[project["name"]] = project

    
    save(projects_planner, namestr(projects_planner, locals()))
    save(tasks_planner, namestr(tasks_planner, locals()))
    save(dates_planner, namestr(dates_planner, locals()))

    print("Objeto adicionado a {} com sucesso!".format(main.lower()))
    

def delete(main):
    with open("projects_planner.json", "r") as project_file:
        projects_planner = load(project_file)
    with open("tasks_planner.json", "r") as tasks_file:
        tasks_planner = load(tasks_file)
    with open("dates_planner.json", "r") as dates_file:
        dates_planner = load(dates_file)
    available_tasks = return_available(tasks_planner, True)
    available_projects = return_available(projects_planner, True)
    if main == "Tasks":
        question = {
            "type": "checkbox",
            "name": "delete",
            "message": "Selecione as tasks a serem deletadas:",
            "choices": available_tasks,
        }
        deletions = {"delete": []}
        while not deletions["delete"]:
            deletions = prompt(question)
        deletions = deletions["delete"]
        if len(deletions) == 1 and deletions[0] == "Voltar":
            secondary_menu(main)
            return
        try:
            del deletions[deletions.index("Voltar")]
        except:
            pass
        for deletion in deletions:
            count_proj = 0
            count_date = 0
            for task in projects_planner[tasks_planner[deletion]["project"]]["tasks"]:
                if task["name"] == deletion:
                    del projects_planner[tasks_planner[deletion]["project"]]["tasks"][count_proj]
                count_proj += 1
            if len(projects_planner[tasks_planner[deletion]["project"]]["tasks"]) == 0 and tasks_planner[deletion]["project"] != "Avulso":
                should = "h"
                while should.lower() not in ("n", "nao", "s", "sim"):
                    should = input('Deletar projeto "{}"? (s/n)'.format(tasks_planner[deletion]["project"]))
                if should in ("s", "sim"):
                    del projects_planner[tasks_planner[deletion]["project"]]
            for task in dates_planner[tasks_planner[deletion]["deadline"]]:
                if task["name"] == deletion:
                    del dates_planner[tasks_planner[deletion]["deadline"]][count_date]
                count_date += 1
            del tasks_planner[deletion]

    elif main == "Projetos":
        question = {
            "type": "checkbox",
            "name": "delete",
            "message": "Selecione os projetos a serem deletados:",
            "choices": available_projects,
        }
        deletions = {"delete": []}
        while not deletions["delete"]:
            deletions = prompt(question)
        deletions = deletions["delete"]
        if len(deletions) == 1 and deletions == "Voltar":
            secondary_menu(main)
            return
        try:
            del deletions[deletions.index("Voltar")]
        except:
            pass
        for deletion in deletions:
            for task in projects_planner[deletion]["tasks"]:
                for i in tasks_planner:
                    if task["name"] == tasks_planner[i]["name"]:
                        count = 0
                        for j in dates_planner[tasks_planner[i]["deadline"]]:
                            if j["name"] == tasks_planner[i]["name"]:
                                del dates_planner[tasks_planner[i]["deadline"]][count]
                            count += 1
                del tasks_planner[task["name"]]
            del projects_planner[deletion]

    
    save(projects_planner, namestr(projects_planner, locals()))
    save(tasks_planner, namestr(tasks_planner, locals()))
    save(dates_planner, namestr(dates_planner, locals()))

    print("Objetos de {} deletados com sucesso!". format(main.lower()))


def conclude(main):
    with open("projects_planner.json", "r") as project_file:
        projects_planner = load(project_file)
    with open("tasks_planner.json", "r") as tasks_file:
        tasks_planner = load(tasks_file)
    with open("dates_planner.json", "r") as dates_file:
        dates_planner = load(dates_file)
    available_tasks = return_available(tasks_planner, True)
    available_projects = return_available(projects_planner, True)
    if main == "Tasks":
        question = {
            "type": "checkbox",
            "name": "conclude",
            "message": "Selecione as tasks a serem concluidas:",
            "choices": available_tasks,
        }
        conclusions = {"conclude": []}
        while not conclusions["conclude"]:
            conclusions = prompt(question)
        conclusions = conclusions["conclude"]
        if len(conclusions) == 1 and conclusions[0] == "Voltar":
            secondary_menu(main)
            return
        try:
            del conclusions[conclusions.index("Voltar")]
        except:
            pass
        for conclusion in conclusions:
            count_date = 0
            for task in projects_planner[tasks_planner[conclusion]["project"]]["tasks"]:
                if task["name"] == conclusion:
                    task["done"] = True
            if len(return_available(projects_planner[tasks_planner[conclusion]["project"]]["tasks"], False)) == 0 and tasks_planner[conclusion]["project"] != "Avulso":
                projects_planner[tasks_planner[conclusion]["project"]]["done"] = True
            for task in dates_planner[tasks_planner[conclusion]["deadline"]]:
                if task["name"] == conclusion:
                    del dates_planner[tasks_planner[conclusion]["deadline"]][count_date]
                count_date += 1
            tasks_planner[conclusion]["done"] = True

    elif main == "Projetos":
        question = {
            "type": "checkbox",
            "name": "conclude",
            "message": "Selecione os projetos a serem concluidos:",
            "choices": available_projects,
        }
        conclusions = {"conclude": []}
        while not conclusions["conclude"]:
            conclusions = prompt(question)
        conclusions = conclusions["conclude"]
        if len(conclusions) == 1 and conclusions == "Voltar":
            secondary_menu(main)
            return
        try:
            del conclusions[conclusions.index("Voltar")]
        except:
            pass
        for conclusion in conclusions:
            for task in projects_planner[conclusion]["tasks"]:
                count = 0
                for j in dates_planner[task["deadline"]]:
                    if j["name"] == task["name"]:
                        del dates_planner[task["deadline"]][count]
                    count += 1
                task["done"] = True
                tasks_planner[task["name"]]["done"] = True
            projects_planner[conclusion]["done"] = True

    save(projects_planner, namestr(projects_planner, locals()))
    save(tasks_planner, namestr(tasks_planner, locals()))
    save(dates_planner, namestr(dates_planner, locals()))

    print("Objetos de {} concluidos com sucesso!". format(main.lower()))


def planner():
    with open("dates_planner.json", "r") as dates_file:
        dates_planner = load(dates_file)
    day_deadline = int(input("Quantos dias de planner? "))
    end = datetime.today() + timedelta(days=day_deadline)
    aux_date = {}
    for date in dates_planner:
        if datetime.strptime(date, "%Y-%m-%d") <= end:
            aux_date[date] = dates_planner[date]
        else:
            break
    print(dumps(aux_date, indent=2, ensure_ascii=False))


def secondary_menu(main):
    if main in ("Tasks", "Projetos"):
        option = menu_list([{
            "name": "any",
            "message": "Selecione o que fazer:",
            "choices": ["Adicionar", "Deletar", "Concluir", "Voltar"]
        }])
        if option["any"] == "Adicionar":
            add(main)
            return
        elif option["any"] == "Deletar":
            delete(main)
            return
        elif option["any"] == "Concluir":
            conclude(main)
            return
        else:
            main_menu()
            return
    else:
        planner()
        return


def main_menu():
    main = menu_list([{
        "name": "any",
        "message": "Selecione uma das opções:",
        "choices": ["Tasks", "Projetos", "Planer"]
        }])
    secondary_menu(main["any"])
