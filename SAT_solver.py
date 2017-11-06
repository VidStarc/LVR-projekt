from random import randint
from random import shuffle
import operator

class Solver:
    def __init__(self,file_in,file_out,upgraded=False):
        self.clauseNumber = 0
        self.variableNumber = 0
        self.clauses = {}
        self.eval_dict = {}
        self.possible_variables =[]
        self.random_var_seq = []


        self.read_file(file_in)
        self.make_evaluation_dict()
        #self.find_unique_var()
        #print('zacetna formula ',self.clauses)
        #self.simplify_by(3,True)
        #print('konec',self.clauses,self.eval_dict)

        self.find_random_var_seq()
        #print("random seq",self.random_var_seq)
        if upgraded:
            solvable = self.solve_upgraded(0)
        else: solvable = self.solve([],{},0)
        self.result(solvable,file_out)
        #print('final',self.eval_dict)
        #print(solvable)




    def result(self,solv,file):
        f = open(file,'w')
        if not solv: f.write('0')
        else:
            for i in self.eval_dict:
                if self.eval_dict[i] == True:
                    f.write(str(i) + ' ')
                elif self.eval_dict[i] == False:
                    f.write(str(-i) + ' ')



    def find_random_var_seq(self,check = False):
        if check:
            freq_dict = {}
            for i in self.possible_variables:
                freq_dict[i] = 0
            for i in self.clauses:
                for j in self.clauses[i]:
                    freq_dict[j] += 1

            #print('gelllleeeeeeeeeej',freq_dict )
            sorted_l = sorted(freq_dict.items(), key=operator.itemgetter(1),reverse=True)
            sort_elem,_ = zip(*sorted_l)
            self.random_var_seq = sort_elem
        else:
            self.random_var_seq = list(range(1,self.variableNumber+1))
            shuffle(self.random_var_seq)
            #self.random_var_seq = [2,5,3,4,1]

    def read_file(self,file_in):
        with open(file_in) as f:
            lines = f.readlines()
            ind = 0
            for i,l in enumerate(lines):
                if l[0] == 'c': continue
                else:
                    ind = i
                    break
            help = lines[ind].split()
            self.variableNumber = int(help[2])
            self.clauseNumber = int(help[3])
            lines = lines[ind+1:]
            for i,l in enumerate(lines):
                line = l.split()
                line = list(map(int, line))
                self.clauses[i] = line[:-1]

            #print('glej',self.clauses,self.clauseNumber,self.variableNumber)



    def make_evaluation_dict(self):
        self.eval_dict = {a+1: None for a in range(self.variableNumber)}
        self.possible_variables = [a+1 for a in range(self.variableNumber)] + [-a-1 for a in range(self.variableNumber)]

    def find_unit_clause(self):
        for i,clause in self.clauses.items():
            if len(clause) == 1:
                return self.clauses[i][0]
        return False

    def rand_variable(self):
        possible_vars = set(sum(list(self.clauses.values()),[]))
        return possible_vars[randint(0, len(possible_vars)-1)]


    def repair(self,add_clauses,ad_variables):
        #print(add_clauses,ad_variables)
        for i in add_clauses:
            self.clauses[i] = add_clauses[i]
        for i in ad_variables[1]:
            self.clauses[i].append(ad_variables[0])
        self.eval_dict[abs(ad_variables[0])]=None


    # var is a if var = true and -a if a = false!!!
    def simplify_by(self,var,value):
        #print('ja')
        self.eval_dict[abs(var)] = value
        delete_clauses = []
        save_deleted_clauses = {}
        save_deleted_vars_from_clauses = (-var,[])
        for i,clause in self.clauses.items():
            if var in clause:
                delete_clauses += [i]
                continue
            if -var in clause:
                if len(self.clauses[i])<2:
                    self.repair(save_deleted_clauses,save_deleted_vars_from_clauses)
                    return None,None
                ind = clause.index(-var)
                save_deleted_vars_from_clauses[1].append(i)
                self.clauses[i].pop(ind)

        for k in delete_clauses:
            save_deleted_clauses[k] = self.clauses[k]
            self.clauses.pop(k)
        #print('deleted info',save_deleted_clauses,save_deleted_vars_from_clauses)
        return save_deleted_clauses,save_deleted_vars_from_clauses

    def solve_upgraded1(self,cur_index):
        cur_var = self.random_var_seq[cur_index]
        check = self.trans_var_boolean(cur_var)

        new_deleted_clauses,new_deleted_vars = self.simplify_by(cur_var,check)
        if new_deleted_clauses != None:
            check_bool = self.solve_upgraded(cur_index+1)
            if check_bool: return True
            self.repair(new_deleted_clauses,new_deleted_vars)

        new_deleted_clauses,new_deleted_vars = self.simplify_by(-cur_var,not check)
        if new_deleted_clauses != None:
            check_bool = self.solve_upgraded(cur_index+1)
            if check_bool: return True
            self.repair(new_deleted_clauses,new_deleted_vars)
            return False
        return False

    def solve_upgraded(self,cur_index):
        if not self.clauses: return True
        if cur_index >= self.variableNumber: return False

        v = self.find_unit_clause() #todo: popravi ker v je lahko negativen in ga pa ni na random listi
        # if there is unit clause than simplify by that literal
        if not v:
            return self.solve_upgraded1(cur_index)
        else:
            check = self.trans_var_boolean(v)
            new_deleted_clauses,new_deleted_vars = self.simplify_by(v,check)
            if new_deleted_clauses != None:
                check_bool = self.solve_upgraded(cur_index+1)
                if check_bool: return True
                self.repair(new_deleted_clauses,new_deleted_vars)
            return False

    def solve(self,deleted_clauses,deleted_vars,cur_index):
        #print('from solve',self.eval_dict,self.clauses)
        allowed = None
        if not self.clauses: return True
        if cur_index >= self.variableNumber: return False
        cur_var = self.random_var_seq[cur_index]
        if cur_var == 1:
            m = 3
        v = self.find_unit_clause() #todo: popravi ker v je lahko negativen in ga pa ni na random listi
        # if there is unit clause than simplify by that literal
        if v != False:
           ind = self.random_var_seq.index(abs(v))
           if v<0: allowed = False
           else: allowed = True
           self.random_var_seq[ind],self.random_var_seq[cur_index] = cur_var,abs(v)
           #self.simplify_by(v,self.trans_var_boolean(v))
        # else pick a random one
        rand_var = self.random_var_seq[cur_index]
        if allowed or allowed is None:
            new_deleted_clauses,new_deleted_vars = self.simplify_by(rand_var,True)
            if new_deleted_clauses != None:
                check_bool = self.solve(new_deleted_clauses,new_deleted_vars,cur_index+1)
                if check_bool: return True
                self.repair(new_deleted_clauses,new_deleted_vars)

        if not allowed or allowed is None:
            new_deleted_clauses,new_deleted_vars = self.simplify_by(-rand_var,False)

            #if not self.clauses: return True
            if new_deleted_clauses != None:
                check_bool = self.solve(new_deleted_clauses,new_deleted_vars,cur_index+1)
                if check_bool: return True
                self.repair(new_deleted_clauses,new_deleted_vars)
                return False
        return False

    def trans_var_boolean(self,var):
        if var<0: return False
        else: return True

#Solver("sudoku_hard.txt","sudoku_hard_sol.txt")
#ss = Solver("example.txt","sudoku_hard_sol.txt")
# not useful in practice
"""
    def find_unique_var(self):
        set_clauses = set(sum(self.clauses,[]))
        for a in self.possible_variables:
            if a not in set_clauses:
                if a < 0: self.simplify_by(-a,True)
                else: self.simplify_by(-a,False)
"""
