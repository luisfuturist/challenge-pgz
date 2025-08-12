import uuid
from collections import defaultdict
from typing import List, Set, Type

# region ECS


class Entity:
    """A simple class to represent an entity. It's just a unique ID."""

    def __init__(self):
        self.uid = str(uuid.uuid4())

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        return isinstance(other, Entity) and self.uid == other.uid


class Component:
    """
    A base class for all components. Components are data containers.
    """

    pass


class System:
    """
    A base class for all systems. Systems contain the logic.
    """

    def __init__(self, world):
        self.world = world

    def update(self, dt: float):
        """
        The main update logic for the system. This method will be called for each
        frame.
        'dt' is the delta time.
        """
        pass

    def draw(self):
        """
        The main rendering logic for the system. This method will be called for each
        frame.
        """
        pass


class World:
    """
    The main class that manages entities, components, and systems.
    It orchestrates the entire simulation.
    """

    def __init__(self):
        self.entities = set()
        # A dictionary to store components.
        # { component_type: { entity_id: component_instance } }
        self.components = defaultdict(dict)
        self.systems = []

    def create_entity(self) -> Entity:
        """Creates a new entity and adds it to the world."""
        entity = Entity()
        self.entities.add(entity)
        return entity

    def destroy_entity(self, entity: Entity):
        """Removes an entity and all its components from the world."""
        if entity in self.entities:
            self.entities.remove(entity)
            for component_type in list(self.components.keys()):
                if entity in self.components[component_type]:
                    del self.components[component_type][entity]

    def add_component(self, entity: Entity, component: Component):
        """Adds a component to an entity."""
        component_type = type(component)
        self.components[component_type][entity] = component

    def get_component(self, entity: Entity, component_type: Type[Component]):
        """Retrieves a component from an entity."""
        return self.components[component_type].get(entity)

    def remove_component(self, entity: Entity, component_type: Type[Component]):
        """Removes a component from an entity."""
        if entity in self.components[component_type]:
            del self.components[component_type][entity]

    def add_system(self, system: System):
        """Adds a system to the world."""
        self.systems.append(system)

    def remove_system(self, system: System):
        """Removes a system from the world."""
        self.systems.remove(system)

    def get_matching_entities(
        self, component_types: Set[Type[Component]]
    ) -> List[Entity]:
        """
        Returns a list of entities that have all the specified components.
        This is a key part of the ECS pattern.
        """
        matching_entities = set(self.entities)
        for component_type in component_types:
            if not self.components[component_type]:
                return []
            matching_entities &= set(self.components[component_type].keys())
        return list(matching_entities)

    def update(self, dt: float):
        """The main loop that updates all systems."""
        for system in self.systems:
            system.update(dt)

    def draw(self):
        """Run only render systems for drawing"""
        for system in self.systems:
            system.draw()


# endregion
