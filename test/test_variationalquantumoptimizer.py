import unittest
import numpy as np
from functools import partial
from variationaltoolkit.objectives import maxcut_obj
from variationaltoolkit import VariationalQuantumOptimizer

class TestVariationalQuantumOptimizer(unittest.TestCase):

    def setUp(self):
        self.varform_description = {'name':'RYRZ', 'num_qubits':4, 'depth':3}
        self.backend_description={'package':'mpsbackend'}
        self.execute_parameters={'shots':1000}
        self.optimizer_parameters={'maxiter':50, 'disp':True}
        w = np.array([[0,1,1,0],[1,0,1,1],[1,1,0,1],[0,1,1,0]])
        self.obj = partial(maxcut_obj, w=w) 

    def test_maxcut(self):
        import logging; logging.disable(logging.CRITICAL)
        varopt = VariationalQuantumOptimizer(
                self.obj, 
                'COBYLA', 
                optimizer_parameters=self.optimizer_parameters, 
                varform_description=self.varform_description, 
                backend_description=self.backend_description, 
                execute_parameters=self.execute_parameters)
        varopt.optimize()
        res = varopt.get_optimal_solution()
        self.assertEqual(res[0], -4)
        self.assertTrue(np.array_equal(res[1], np.array([1,0,0,1])) or np.array_equal(res[1], np.array([0,1,1,0])))
        logging.disable(logging.NOTSET)

    def test_maxcut_seqopt(self):
        import logging; logging.disable(logging.CRITICAL)
        varopt = VariationalQuantumOptimizer(
                self.obj, 
                'SequentialOptimizer', 
                optimizer_parameters=self.optimizer_parameters, 
                varform_description=self.varform_description, 
                backend_description=self.backend_description, 
                execute_parameters=self.execute_parameters)
        varopt.optimize()
        res = varopt.get_optimal_solution()
        self.assertEqual(res[0], -4)
        self.assertTrue(np.array_equal(res[1], np.array([1,0,0,1])) or np.array_equal(res[1], np.array([0,1,1,0])))
        logging.disable(logging.NOTSET)

if __name__ == '__main__':
    unittest.main()
