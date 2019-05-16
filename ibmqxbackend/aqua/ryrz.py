# -*- coding: utf-8 -*-

# Copyright 2018 IBM.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

import numpy as np
from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister

from .variational_form import VariationalForm


class VarFormRYRZ(VariationalForm):
    """Layers of Y+Z rotations followed by entangling gates."""

    RYRZ_CONFIGURATION = {
        'name': 'RYRZ',
        'description': 'RYRZ Variational Form',
        'input_schema': {
            '$schema': 'http://json-schema.org/schema#',
            'id': 'ryrz_schema',
            'type': 'object',
            'properties': {
                'depth': {
                    'type': 'integer',
                    'default': 3,
                    'minimum': 1
                },
                'entanglement': {
                    'type': 'string',
                    'default': 'full',
                    'oneOf': [
                        {'enum': ['full', 'linear']}
                    ]
                },
                'entangler_map': {
                    'type': ['object', 'null'],
                    'default': None
                }
            },
            'additionalProperties': False
        }
    }

    def __init__(self, configuration=None):
        super().__init__(configuration or self.RYRZ_CONFIGURATION.copy())
        self._num_qubits = 0
        self._depth = 0
        self._entangler_map = None
        self._initial_state = None

    def init_args(self, num_qubits, depth, entangler_map=None,
                  entanglement='linear', initial_state=None):
        """
        Args:
            num_qubits (int) : number of qubits
            depth (int) : number of rotation layers
            entangler_map (dict) : dictionary of entangling gates, in the format
                                    { source : [list of targets] },
                                    or None for full entanglement.
            entanglement (str): 'full' or 'linear'
            initial_state (InitialState): an initial state object
        """
        self._num_parameters = num_qubits * (depth + 1) * 2
        self._bounds = [(-np.pi, np.pi)] * self._num_parameters
        self._num_qubits = num_qubits
        self._depth = depth
        if entangler_map is None:
            self._entangler_map = VariationalForm.get_entangler_map(entanglement, num_qubits)
        else:
            self._entangler_map = VariationalForm.validate_entangler_map(entangler_map, num_qubits)
        self._initial_state = initial_state

    def construct_circuit(self, parameters, q=None):
        """
        Construct the variational form, given its parameters.

        Args:
            parameters (numpy.ndarray): circuit parameters
            q (QuantumRegister): Quantum Register for the circuit.

        Returns:
            QuantumCircuit: a quantum circuit with given `parameters`

        Raises:
            ValueError: the number of parameters is incorrect.
        """
        if len(parameters) != self._num_parameters:
            raise ValueError('The number of parameters has to be {}'.format(self._num_parameters))

        c = ClassicalRegister(self._num_qubits, name='c')
        if q is None:
            q = QuantumRegister(self._num_qubits, name='q')
        if self._initial_state is not None:
            circuit = self._initial_state.construct_circuit('circuit', q)
        else:
            circuit = QuantumCircuit(q,c)

        param_idx = 0
        for qubit in range(self._num_qubits):
            circuit.u3(parameters[param_idx], 0.0, 0.0, q[qubit])
            circuit.u1(parameters[param_idx+1], q[qubit])
            # circuit.ry(parameters[param_idx], q[qubit])
            # circuit.rz(parameters[param_idx+1], q[qubit])
            param_idx += 2

        for block in range(self._depth):
            circuit.barrier(q)
            for node in self._entangler_map:
                for target in self._entangler_map[node]:
                    circuit.u2(0.0, np.pi, q[target])  # h
                    circuit.cx(q[node], q[target])
                    circuit.u2(0.0, np.pi, q[target])  # h
                    # circuit.cz(q[node], q[target])
            for qubit in range(self._num_qubits):
                circuit.u3(parameters[param_idx], 0.0, 0.0, q[qubit])
                circuit.u1(parameters[param_idx+1], q[qubit])
                # circuit.ry(parameters[param_idx], q[qubit])
                # circuit.rz(parameters[param_idx+1], q[qubit])
                param_idx += 2
        circuit.barrier(q)

        return circuit
