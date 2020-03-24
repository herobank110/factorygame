"""Defines all actor components for modular use.

Actor components can be created using the static method `create_engine_object`
of `GameplayUtilities`. This can be done in an actor's constructor so that
variables of the component can be set.

Currently there is no tick support for engine objects, so those components
that require tick events must be called manually by the actor. There is also
no automatic owning actor configuration, so this must be set each time the
component is created by the actor.

TODO: automatically set owning actor and tick events for components
TODO: create actor component base class for extra functionality
"""
