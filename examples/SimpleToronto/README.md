# GeoSIR Epidemics Model

## Summary

This is a geoversion of a simple agent-based pandemic SIR model, as an example to show the capabilities of mesa-geo.

It uses geographical data of Toronto's regions on top of a an Leaflet map to show the location of agents (in a continuous space).

Person agents are initially located in random positions in the city, then start moving around unless they die.
A fraction of agents start with an infection and may recover or die in each step.
Susceptible agents (those who have never been infected) who come in proximity with an infected agent may become infected.

Neighbourhood agents represent neighbourhoods in the city, and become hot-spots (colored red) if there are infected agents inside them.
