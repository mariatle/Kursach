import numpy as np
from particleswarm import Swarm

class SwarmSchwefel(Swarm):
    def __init__(
        self,
        swarmsize: int,
        minvalues: list[float],
        maxvalues: list[float],
        currentVelocityRatio: float,
        localVelocityRatio: float,
        globalVelocityRatio: float,
    ):
        super().__init__(
            swarmsize,
            minvalues,
            maxvalues,
            currentVelocityRatio,
            localVelocityRatio,
            globalVelocityRatio,
        )

    def _finalFunc(self, position):
        function = 418.9829 * len(position) - sum(position * np.sin(np.sqrt(np.abs(position))))
        penalty = self._getPenalty(position, 10000.0)
        return function + penalty
