import os
from fastapi import HTTPException
import jinja2
from security.settings import settings
import subprocess
import json
import requests
import time

from utils.helper import create_directory


def create_n_project(name: str, description: str):
    # create project using Nuclio's REST API 202 even project is already there
    
    deploy_url = f"{settings.N_URL}/api/projects"
    headers = {"Content-Type": "application/json"}
    data = {
        "metadata": {
            "name": name,
            "namespace": "nuclio"
        },
        "spec": {
            "description": description
        }
    }
    
    print(deploy_url, headers, data)

    response = requests.post(deploy_url, headers=headers, data=json.dumps(data))
    print(response)
    return response



def wait_for_function_ready( schema_name, table_name):
    url = f'{settings.N_URL}/api/functions/{schema_name}-{table_name}'
    
    unHealthyCount=0
    
    while True:
        health_response = requests.get(url)
        if health_response.status_code != 200:
            print(f"Error: Received status code {health_response.status_code}")
            break
        
        health_status = health_response.json().get('status', {}).get('state')
        
        if health_status == 'ready':
            print("Function is ready.")
            break
        elif health_status == 'unhealthy' and unHealthyCount==3:
            raise HTTPException(status_code=404, detail=f"Function is in an unexpected state: {health_status}")

        elif health_status == 'unhealthy' and unHealthyCount!=3:
            unHealthyCount+=1
            
        elif health_status != 'building':
            print(f"Function is in an unexpected state: {health_status}")
            break
        
        print("Function is still building. Waiting for 2 seconds before checking again...")
        time.sleep(2)

    return health_response.json()



def create_python_function(schema_name: None, table_name: None):
    
    schema_name = schema_name
    table_name = table_name
    
    namespace = "nuclio"
    filename_without_extension = "main"
    numWorkers = 1
    
    # 
    
    static_dir = "static"
    test_dir = os.path.join(static_dir, "test")
    function_dir = os.path.join(test_dir, 'function')
    create_directory(test_dir)
    create_directory(function_dir)
    
    template_dir = "static/templates/nuclio/python"
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    
    
    template = env.get_template("crud_template.py.j2")
    rendered_function_content = template.render(
        n_database_url=settings.N_DATABASE_URL,
        schema_name=schema_name,
        table_name=table_name,
    )
    
    
    with open(f"static/test/function/main.py", "w") as f:
        f.write(rendered_function_content)
        f.close()
        
        
    dtemplate = env.get_template("dockerbuildfile.j2")
    rendered_dockerfile_content = dtemplate.render(    
        database_url = settings.N_DATABASE_URL
    )
    
    with open(f"static/test/Dockerfile", "w") as f:
        f.write(rendered_dockerfile_content)
        f.close()
        
    ftemplate = env.get_template("function.j2")
    rendered_configuration_content = ftemplate.render(    
        function_name = table_name,
        namespace = namespace,
        filename_without_extension = filename_without_extension,
        numWorkers = numWorkers
    )
    
    with open(f"static/test/function.yaml", "w") as f:
        f.write(rendered_configuration_content)
        f.close()
        
    rtemplate = env.get_template("requirements.j2")
    rendered_requirements_content = rtemplate.render(
        test=""
    )
    
    with open(f"static/test/requirements.txt", "w") as f:
        f.write(rendered_requirements_content)
        f.close()
        
            
    try:
        # Execute the SSH command with subprocess cd test && docker build --tag project-{table_name}:latest .
        result = subprocess.run(f'cd static/test && docker build --tag {schema_name}-{table_name}:latest . ', capture_output=True, text=True, shell=True)
        # if result.returncode==0: 
        print(result)
        # return result.stdout
    except subprocess.CalledProcessError as e:
        raise subprocess.CalledProcessError(f"SSH command failed: {e}") from e
    
    
    
    # Deploy the function using Nuclio's REST API
    deploy_url = f"{settings.N_URL}/api/functions"
    headers = {"Content-Type": "application/json"}
    data = {
        "metadata": {
            "name": f"{schema_name}-{table_name}",
            "namespace": "nuclio",
            "labels": {
                "nuclio.io/project-name": f"{schema_name}"
            },
            "annotations": {}
        },
        "spec": {
            "description": "",
            "disable": False,
            "triggers": {},
            "env": [],
            "loggerSinks": [
                {
                    "level": "debug",
                    "sink": ""
                }
            ],
            "handler": "main:handler",
            "runtime": "python:3.8",
            "build": {
                "image": "",
                "noCache": False,
                "offline": False,
                "dependencies": [],
                "runtimeAttributes": {
                    "repositories": []
                },
                "codeEntryType": "image",
                "mode": "alwaysBuild"
            },
            "resources": {
                "requests": {},
                "limits": {}
            },
            "image": f"{schema_name}-{table_name}:latest"
        }
    }

    response = requests.post(deploy_url, headers=headers, data=json.dumps(data))
    print(response.status_code)
    
    
    
    # health_response = requests.get(f'{settings.N_URL}/api/functions/{schema_name}-{table_name}')
    return wait_for_function_ready(schema_name, table_name)
    
    