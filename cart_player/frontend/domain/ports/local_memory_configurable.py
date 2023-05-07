import abc

from cart_player.backend.api.dtos import LocalMemoryConfiguration


class LocalMemoryConfigurable(abc.ABC):
    """An abstract class for objects that can take into account new LocalMemoryConfiguration objects.

    Subclasses of LocalMemoryConfigurable should implement the `update_local_memory_config` method to specify
    how to update their internal state based on a LocalMemoryConfiguration object.
    """

    @abc.abstractmethod
    def update_local_memory_config(self, local_memory_config: LocalMemoryConfiguration):
        """Update the local memory configuration.

        Args:
            local_memory_config: The LocalMemoryConfiguration object to use for update.
        """
        raise NotImplementedError
