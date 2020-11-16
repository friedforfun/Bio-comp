from functools import total_ordering
import numpy as np
from datetime import datetime, timedelta
import enum


BoundaryPolicy = enum.Enum(
    'BoundaryPolicy', 'RANDOMREINIT REFUSE BOUNCE')


TerminationPolicy = enum.Enum(
    'TerminationPolicy', 'ITERATIONS DURATION CONVERGENCE')

@total_ordering
class FitnessLoc:
    """A comparable class to store a fitness value and vector (position)

        :param location: A vector representing a particles location (or the parameters being optimised)
        :type location: numpy.array
        :param fitness: A value indicating the fitness of the location
        :type fitness: float
    """

    def __init__(self, location, fitness):
        self.location = location
        self.fitness = fitness

    def _is_valid_operand(self, other):
        return(hasattr(other, "fitness") and hasattr(other, "location"))

    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.fitness == other.fitness

    def __lt__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.fitness < other.fitness


class TerminationPolicyManager:
    """An iterator to control the PSO termination behaviour

        :param termination_policy: Sets the policy PSO will use to terminate, can be a list of policies
        :type termination_policy: TerminationPolicy or list(TerminationPolicy)
        :param max_iter: The maximum number of iterations to run PSO, defaults to None
        :type max_iter: int, optional
        :param min_fitness_delta: The smallest fitness change to look for, defaults to None
        :type min_fitness_delta: float/int, optional
        :param time_delta: The time delta object from datetime, defaults to None
        :type time_delta: datetime.timedelta, optional
        :raises ValueError: Max iteration undefined
        :raises ValueError: Time delta undefined
        :raises ValueError: Fitness delta undefined
    """
    def __init__(self, termination_policy, max_iter=None, min_fitness_delta=None, time_delta=None):
        if type(termination_policy) is not list:
            self.termination_policy = [termination_policy]
        else:
            self.termination_policy = termination_policy

        if TerminationPolicy.ITERATIONS in self.termination_policy:
            if max_iter is None:
                raise ValueError('Max iteration undefined')

        if TerminationPolicy.DURATION in self.termination_policy:
            if time_delta is None:
                raise ValueError('Time delta undefined')

        if TerminationPolicy.CONVERGENCE in self.termination_policy:
            if min_fitness_delta is None:
                raise ValueError('Fitness delta undefined')

        # Loop until terminate is true
        self.terminate = False

        # Number of iterations so far
        self.current_iter = 0
        self.max_iter = max_iter

        # The fitness from the last iteration
        self.min_fitness_delta = min_fitness_delta # 0.1
        self.current_fitness_delta = None # 0.15
        self.start_fitness_delta = None # 0.2
        self.got_fitness_delta = False

        self.start_time = datetime.now()
        self.time_delta = time_delta

        self.verbose = True

    #TODO implement logic for a loading bar during optimisation
    def distance_to_termination(self):
        closest_estimate = 0
        iter_estimate = self.current_iter / self.max_iter 
        if self.current_fitness_delta is not None:
            total_distance = self.start_fitness_delta - self.min_fitness_delta
            current_distance = self.start_fitness_delta - self.current_fitness_delta
            current_distance / total_distance


        pass

    def next_iteration(self, fitness_delta=None):
        """Step the termination policy manager forward

        :param fitness_delta: a value representing the delta beween the last best fitness and the current, defaults to None
        :type fitness_delta: float, optional
        :raises ValueError: Fitness delta unspecified - when TerminationPolicy.CONVERGENCE is used and fitness delta has not been updated this iteration
        :raises StopIteration: When the termination condition has been satisfied
        """
        if TerminationPolicy.ITERATIONS in self.termination_policy:
            if self.max_iter < self.current_iter:
                self.terminate = True

        if TerminationPolicy.DURATION in self.termination_policy:
            elapsed = datetime.now() - self.start_time
            if elapsed > self.time_delta:
                self.terminate = True

        if TerminationPolicy.CONVERGENCE in self.termination_policy:
            if fitness_delta is not None and self.min_fitness_delta >= fitness_delta:
                self.terminate = True
            elif self.got_fitness_delta:
                self.got_fitness_delta = False
                if self.min_fitness_delta >= self.current_fitness_delta:
                    self.terminate = True
            else:
                raise ValueError('Fitness delta unspecified')

        self.current_iter += 1

    def update_fitness_delta(self, fitness_delta):
        """Update the fitness delta to a new value

        :param fitness_delta: the current fitness value
        :type fitness_delta: 
        """
        self.current_fitness_delta = fitness_delta
        self.got_fitness_delta = True

    def __iter__(self):
        return self

    def __next__(self):
        self.next_iteration()
        if self.terminate is True:
            raise StopIteration
