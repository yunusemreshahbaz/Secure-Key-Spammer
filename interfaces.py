from abc import ABC, abstractmethod

class IEngine(ABC):
    @abstractmethod
    def set_params(self, *args, **kwargs):
        pass

    @abstractmethod
    def toggle(self):
        pass

    @abstractmethod
    def stop(self):
        pass

class IProfileManager(ABC):
    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def add_or_update(self, name, data):
        pass

    @abstractmethod
    def get_profile(self, name):
        pass
    
    @abstractmethod
    def get_all_names(self):
        pass

class IInputManager(ABC):
    @abstractmethod
    def setup_listeners(self):
        pass
    
    @abstractmethod
    def set_hotkey(self, key):
        pass