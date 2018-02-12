'''
Created on 11 Feb 2018

@author: Bryan
'''
from .potential import Potential
from ..variable import Variable, JointContinuousVariable, DiscreteVariable
from ..parameter import CGParameter
import collections
import numpy as np

class CGPotential(Potential):
    '''
    classdocs
    '''

    def __init__(self, jointVariables, discreteVariable, parameters=None):
        '''
        Constructor
        '''
        if isinstance(jointVariables, JointContinuousVariable):
            jointVariables = list(jointVariables.variables())
        elif isinstance(jointVariables, collections.Iterable):
            jointVariables = list(jointVariables)
        assert isinstance(jointVariables, list)
        self._continuousVariables = jointVariables
        self._discreteVariable = discreteVariable
        self._parameters = parameters
        
    def resetParameters(self):
        cardinality = 1 if self._discreteVariable is None else self._discreteVariable.getCardinality()
        self._parameters = [None]*cardinality
        for i in range(cardinality):
            self._parameters[i] = CGParameter(1./cardinality, len(self._continuousVariables))
    
    def get(self, index):
        return self._parameters[index]
    
    def addParentVariable(self, variable):
        if not isinstance(variable, DiscreteVariable):
            raise ValueError("Parent variable in CGPotential has to be discrete")
        if self._discreteVariable is not None:
            raise Exception("continuous variable can only has one parent")
        self._discreteVariable = variable
        self.resetParameters()
        return self
    
    def removeParentVariable(self, variable):
        assert self._discreteVariable is variable
        self._discreteVariable = None
        self.resetParameters()
        return self
    
    def addHeadVariable(self, variables):
        if isinstance(variables, Variable):
            variables = [variables]
        self._continuousVariables.extend(variables)
        self.resetParameters()
        
    def removeHeadVariable(self, variables):
        if isinstance(variables, Variable):
            variables = [variables]
        for v in variables:
            self._continuousVariables.remove(v)
        self.resetParameters()
        
    @property
    def size(self):
        return len(self._parameters)
    
    def setEntries(self, means, covars):
        """
        means: numpy array KxD
        covars: numpy array KxDxD
        """
        for i in range(self.size):
            self._parameters[i].setEntries(means[i], covars[i])
        
    @property
    def dimension(self):
        return len(self._continuousVariables)
    @property
    def discreteVariable(self):
        return self._discreteVariable
    @property
    def continuousVariables(self):
        return self._continuousVariables
    
    def getEntries(self):
        """
        return 
        means: numpy array KxD
        covars: numpy array KxDxD
        """
        means = np.empty((self.size, self.dimension))
        covars = np.empty((self.size, self.dimension, self.dimension))
        for i in range(self.size):
            mean, covar = self._parameters[i].getEntries()
            means[i] = mean
            covars[i] = covar
        return means, covars
    
    def marginalize(self, variable):
        """
        only support marginalization of discrete variable
        simply return the p
        """
        assert isinstance(variable, DiscreteVariable)
        return self.function()
        
    def function(self):
        p = np.zeros(self.size)
        for i in range(self.size):
            p[i] = self._parameters[i].p
        return p
    
    def multiply(self, p):
        """
        p: array like
        """
        for i in range(self.size):
            self._parameters[i].p = p[i]
        
    def normalize(self, constant=None):
        if constant is None:
            constant = np.sum([x.p for x in self._parameters])
        for i in range(self.size):
            self._parameters[i].p /= constant
        return constant
        
    def clone(self):
        pass
    
    def __str__(self):
        toStr = "CGPotential {\n"
        toStr += "\tcomponent = " + str(self._discreteVariable.getCardinality()) + ";\n"
        toStr += "\tdimension = " + str(len(self._continuousVariables)) + ";\n"
        toStr += "\tdiscrete variable = " + self._discreteVariable.name + ";\n"
        toStr += "\tvariables = { " + " ".join([v.name for v in self._continuousVariables]) + "};\n"
        toStr += "\tcells = [\n" 
        for i in range(self.size):
            toStr += str(self._parameters[i]) 
        toStr += "\t];\n"
        toStr += "}"
        return toStr
        
    