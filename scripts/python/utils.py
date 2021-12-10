import csv, os
import hashlib
import yaml
from frictionless import Package
from dpckan import update_resource
import pymysql
from pathlib import Path
from dotenv import load_dotenv
import json
load_dotenv(dotenv_path=Path('.', '.env'))

def extract_resource(resource_name):
    conn = pymysql.connect(host=os.environ.get('DB_HOST'),
                           user=os.environ.get('DB_USER'),
                           password=os.environ.get('DB_PASSWORD'),
                           database=os.environ.get('DB_DATABASE'),
                           cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    sql_file = open(f'scripts/sql/{resource_name}.sql')
    sql_query = sql_file.read()
    cur.execute(sql_query)

    rows = cur.fetchall()

    colnames = [desc[0] for desc in cur.description]

    with open(f'data/raw/{resource_name}.csv', "w", encoding='utf-8-sig', newline='') as fp:
        myFile = csv.DictWriter(fp, colnames, delimiter=';')
        myFile.writeheader()
        myFile.writerows(rows)

def update_resource_hash(resource_name):
    
    dp = Package('datapackage.json')
    resource = dp.get_resource(resource_name)
    md5_hash = hashlib.md5()
    file = open(resource.path, "rb")
    content = file.read()
    md5_hash.update(content)
    resource.stats.update({'hash': md5_hash.hexdigest()})
    dp.to_json('datapackage.json')

def datasets_create():  
  run_dpckan_dataset('create')

def datasets_update():
  run_dpckan_dataset('update')

def create_datasets_folder():
  if not os.path.exists("datasets"):
    os.system('mkdir datasets')
  from_to_file_path = 'age7.yaml'
  from_to_file = load_yaml_file(from_to_file_path)
  for dataset in from_to_file['consultas'].keys():
    if not os.path.exists(f'datasets/{dataset}'):
      os.system(f'mkdir datasets/{dataset}')
      os.system(f'cp -r templates/* datasets/{dataset}')

def create_datasets_build_folder():
  os.system(f'rm -rf build_datasets/') # Facilitar os teste
  if os.path.exists("build_datasets"):
    print('Pasta datasets_build existente, confira se algum erro ocorreu durante último building.')
  else:
    os.system('mkdir build_datasets')
    from_to_file_path = 'age7.yaml'
    from_to_file = load_yaml_file(from_to_file_path)
    for dataset in from_to_file['consultas'].keys():
      os.makedirs(f'build_datasets/{dataset}/data')
      os.system(f'cp datasets/{dataset}/*.md build_datasets/{dataset}')
      # Lê o arquivo datapackage.json para, entre outros, extrair os recursos daquele conjunto
      base_dp = Package('datapackage.json')
      # Lê o arquivo datasets/conjunto/datapakcage.yaml para extrair os metadados personalizados do conjunto
      target_dp = Package(f'datasets/{dataset}/datapackage.yaml')
      # Inclui no base_dp os metadados extraídos do arquivo datapackage.yaml
      for k in target_dp.keys():
        base_dp[k] = target_dp[k]
      base_dp['name'] = dataset
      base_dp['title'] = from_to_file['consultas'][dataset]['title']
      base_dp['homepage'] = from_to_file['consultas'][dataset]['url']
      fact_tables = from_to_file['consultas'][dataset]['fact_tables']
      target_resources = find_target_resources(from_to_file, fact_tables)
      resources_diff = find_resource_diff(base_dp.resource_names, target_resources)
      base_dp = remove_resources(base_dp, resources_diff)
      base_dp = update_resource_properties(base_dp)
      base_dp.to_json(f'build_datasets/{dataset}/datapackage.json')

def find_resource_diff(original_resources, target_resources):
  resources_diff = [i for i in original_resources if not i in target_resources]
  return resources_diff

def remove_resources(base_dp, resources_diff):
  for resource in resources_diff:
    base_dp.remove_resource(resource)
  return base_dp

def update_resource_properties(base_dp):
  for resource in base_dp.resource_names:
    path = base_dp.get_resource(resource).path
    base_dp.get_resource(resource).schema.expand()
    base_dp.get_resource(resource).dialect.expand()
    if not os.path.exists(path):
      # Excluir recurso se arquivo de dados não existir
      print(f'Arquivo de dados do recurso "{resource}" do dataset "{base_dp.name}" ausente.')
      base_dp.remove_resource(resource)
    else:
      new_path = f'build_datasets/{base_dp.name}/{path}'
      # base_dp.get_resource(resource).path = new_path
      os.system(f'cp {path} {new_path}')
  return base_dp

def load_yaml_file(file_path):
  yaml_dict_content = file_path
  yaml_dict_content = open(yaml_dict_content, encoding='utf-8').read()
  yaml_dict_content = yaml.load(yaml_dict_content, Loader=yaml.FullLoader)
  return yaml_dict_content

def find_target_resources(from_to_file, fact_tables):
  target_resources = []
  for fact_table in fact_tables:
    target_resources.append(fact_table)
    if fact_table in from_to_file['fact_tables'].keys():
      for dim_table in from_to_file['fact_tables'][fact_table]:
        if dim_table not in target_resources:
          target_resources.append(dim_table)
    else:
      print(f"{fact_table} não existente em data['fact_tables']")
  return target_resources

def run_dpckan_dataset(action):
  path = 'build_datasets'
  folder = os.fsencode(path)
  for sub_folder in os.listdir(folder):
    folder_name = str(sub_folder).split('\'')[1]
    datapackage_path = f'build_datasets/{folder_name}/datapackage.json'
    new_datapackage_ckan_hosts = ''
    # os.system(f'dpckan dataset create -dp {datapackage_path}')
    # ipdb.set_trace(context=10)
    if action == 'create':
      os.system(f'dpckan dataset create -dp {datapackage_path}')
      new_datapackage_ckan_hosts = Package(datapackage_path)["ckan_hosts"]
    if action == 'update':
      os.system(f'dpckan dataset update -dp {datapackage_path}')
    datapackage_yaml_path = f'datasets/{folder_name}/datapackage.yaml'
    datapackage_yaml = load_yaml_file(datapackage_yaml_path)
    with open(datapackage_yaml_path, 'w') as f:
      datapackage_yaml['ckan_hosts'] = new_datapackage_ckan_hosts
      yaml.dump(datapackage_yaml, f)
