# Packager notes for hipBLASLt

## Extraneous CPU libraries

The `hipblaslt-bench` executable links to some libraries that might raise some
eyebrows:
- OpenMP
- blis

They're NOT used when running the GPU optimized kernel and exist solely for the
purpose of benchmarking, serving as the known-correct CPU implementation to
compare against.
