# GeoSchelling Segregation Model with Point Agents

## Summary

This is a geoversion of a simplified Schelling example.

**GeoSpace**

The NUTS-2 regions are considered as a shared definition of neighborhood among all agents, instead of a locally defined neighborhood such as Moore or von Neumann.

**GeoAgent**

Each agent resides in a randomly assigned region, and checks the color ratio of its region against a pre-defined "happiness" threshold at every step. If the ratio falls below the threshold, the agent is found to be "unhappy", and randomly moves to another region. In this example, agents are represented as points, with locations randomly chosen within their regions.

## How to run

To run the model interactively, run `mesa runserver` in this directory. e.g.

```bash
mesa runserver
```

Then open your browser to [http://127.0.0.1:8521/](http://127.0.0.1:8521/) and press `Start`.
