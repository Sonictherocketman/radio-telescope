import pickle

from ..models.observation import Observation


def write(path, observation: Observation):
    with open(path, 'wb') as f:
        pickle.dump(observation, f)


def read(path) -> Observation:
    with open(path, 'rb') as f:
        return pickle.load(f)
