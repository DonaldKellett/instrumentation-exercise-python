# instrumentation-exercise-python

[Prometheus](https://prometheus.io/) instrumentation exercise in Python 3. Based on [juliusv/instrumentation-exercise](https://github.com/juliusv/instrumentation-exercise)

## Overview

The main branch contains the original server, the instrumented branch contains the instrumented version of the server which exports Prometheus metrics under the path `/metrics` but is otherwise equivalent to the original server.

## Dependencies

- [prometheus-client](https://github.com/prometheus/client_python)

## Resources

Learn about Prometheus:

- [Official docs](https://prometheus.io/docs/)
- [LFS241: Monitoring Systems and Services with Prometheus](https://training.linuxfoundation.org/training/monitoring-systems-and-services-with-prometheus-lfs241/)

## License

[MIT](./LICENSE)
