# Circuit Group Assignments

Circuits can be assigned to [Circuit groups](./circuitgroup.md) to indicate Fallback Circuits. For instance, three circuits, each belonging to a different provider, may each be assigned to the same Circuit group. Each of these assignments would typically receive a different priority.

Circuits are assigned to Circuit groups under the Circuit Group detail view.

## Fields

### Group

The [Circuit group](./circuitgroup.md) being assigned.

### Circuit

The [Circuit](./circuit.md) that is being assigned to the group.

### Priority

A selection (Primary, Secondary, Tertiary) indicating the circuit's priority for being elected as the master/primary node in the group.
