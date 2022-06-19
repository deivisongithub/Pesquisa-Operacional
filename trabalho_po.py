"""
Trabalho PO.ipynb

Original file is located at
    https://colab.research.google.com/drive/1iMB9kfIDvf14njX8IOF2bvJmR7_dlVdh

Aluno: ARTUR LUIS BRITO GURJAO   /   Matricula: 20200024903
Aluno: DEIVISON RODRIGUES JORDAO /   Matricula: 20200023728

"""

from mip import *
import numpy as np
import re

def read_txt():  #CAMINHO DO ARQUVIVO EM STRING, EXEMPLO: 'projeto.txt'

  global vars
  global rests
  global list_of_coef_obj
  global list_of_rest

  caminho = input('Insira o caminho do arquivo txt formatado: ')

  l = []
  with open(caminho) as file:
    for line in file:
        for i in re.findall(r'\d+', line):
            l.append(i)
  
  vars = int(l[0])
  rests = int(l[1])
  for i in range(2, 2+vars):
    list_of_coef_obj.append(int(l[i]))

  count = 0
  aux = []
  for i in range(2+vars, len(l)):
    if count == vars:
      aux.append(int(l[i]))
      list_of_rest.append(aux)
      aux = []
      count = 0
    else:
      aux.append(int(l[i]))
      count += 1

def create_model(vars, rests, list_of_coef_obj, list_of_rest):

  model = Model(sense=MAXIMIZE)

  x = [model.add_var(var_type="CONTINUOUS",
                      lb=0, ub=1, name="x_" + str(i)) for i in range(vars)]

  model.objective = xsum(list_of_coef_obj[i]*x[i]
                           for i in range(vars))

  for i in range(rests):
      model += xsum(list_of_rest[i][j]*x[j] for j in range(vars)) <= list_of_rest[i][-1]

  return model

def solver(model):
  model.optimize()
  params = {}
  params["objective"] = model.objective_value
  params["vars"] = model.vars

  return params

def branch_and_bound(model):
  nodes = [model]
  global primal
  primal = 0

  global optimal_model

  while nodes != []:
    model_solver = solver(nodes[0])
    aux = bound(nodes[0])
    if aux == 'INVIABILIDADE' or aux == 'LIMITE':
      nodes.pop(0)
    elif aux == 'INTEGRALIDADE':
      if model_solver["objective"] >= primal:
        optimal_model = nodes[0]
        primal = model_solver["objective"]
      nodes.pop(0)
    elif aux == 'FRACIONÁRIO':
      nodes.append(branch(nodes[0], model_solver["vars"])[0])
      nodes.append(branch(nodes[0], model_solver["vars"])[1])
      nodes.pop(0)
    print(nodes)

def bound(model):
  aux_solver = solver(model)
  count_int = 0
  global primal

  if aux_solver["objective"] == None:
    return 'INVIABILIDADE'

  for i in aux_solver["vars"]:
    if i.x.is_integer():
      count_int += 1
  
  if count_int == vars:
    return 'INTEGRALIDADE'

  if aux_solver["objective"] <= primal:
    return 'LIMITE'
  return 'FRACIONÁRIO'

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def branch(model, values_solution):
  # escolhe a variável para aplicação das restrições
  var_branch = values_solution[find_nearest([i.x for i in values_solution], 0.5)]

  # NÓ que terá a restrição var == 0
  model_0 = model.copy()
  model_0 += var_branch == 0

  # NÓ que terá a restrição var == 1
  model_1 = model.copy()
  model_1 += var_branch == 1

  return [model_0, model_1]

def main():

  read_txt()

  test = create_model(vars, rests, list_of_coef_obj, list_of_rest)

  branch_and_bound(test)
  solved = solver(optimal_model)

  #print soluçao otima
  for i in solved["vars"]:
    print(i.name, ' = ', i.x)
  print('Z = ',solved["objective"])

#VARIAVEIS GLOBAIS

primal = 0 #inferior
optimal_model = 0
vars = 0
rests = 0
list_of_coef_obj = []
list_of_rest = []

#CHAMADO DA FUNÇÂO MAIN
main()