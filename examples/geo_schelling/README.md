# GeoSchelling Segregation Model

## Summary

This is a geoversion of a simplified Schelling example. For the original implementation details please see the Mesa Schelling examples.
Instead of a regular grid it uses European NUTS-2 regions as location for majority and minority opinions.
For a region to be happy it only needs to have more similar neighbors than unsimilar ones.

## How to Run

To run the model interactively, run `mesa runserver` in this directory. e.g.

```bash
mesa runserver
```

Then open your browser to [http://127.0.0.1:8521/](http://127.0.0.1:8521/) and press `Start`.
