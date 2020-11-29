# Profiller Feature of the Software

The first step toward a fast implementation of a program is profiling to find out where your code spends its time. The key point is to only optimize functions that are actually slow or are called extensively. Profilers can collect several types of information: timing, function calls, interruptions, cache faults… In our case, we are going to focus our attention on timing and function calls.

There are two types of profiller that can be used for optimization of the program:

1. Determinisic Profiling
2. Statistical Profiling

## Deterministic Vs Statistical

1. Deterministic Profiling: All events are monitored. It provides accurate information but has a big impact on performance (overhead). It means the code run slower under profiling. Its use in production systems is often impractical. This type of profiling is suitable for small functions. (cProfile)

2. Statistical profiling: Sampling the execution state at regular intervals to compute indicators. This method is less accurate, but it also reduces the overhead. Examples: py-spy, pyinstrument

[Source](https://medium.com/@antoniomdk1/hpc-with-python-part-1-profiling-1dda4d172cdf)

For implementing every option mentioned for profiling, the documnetation avaialble on web should be checked. 

For sake of our project we are using cProfile.

## cProfile

Python comes with two modules for deterministic profiling: cProfile and profile. Both are different implementations of the same interface. The former is a C extension with relatively small overhead, and the latter is a pure Python module. As the official documentation says, the module profile would be suitable when we want to extend the profiler in some way. Otherwise, cProfile is preferred for long-running programs.

Option is provided in both interface and Firmware to profile the structure. It should be noted that the profiller result may not be very human readable. Therefore, proper solution for both linux,mac and windows is selected for visualization purposes. 

## Visualization

[gprof2dot](https://github.com/jrfonseca/gprof2dot) is used, which converts the output of cProfile to a dot graph. It is compatible with python 2 and 3 (tested). Therefore, it can be used for both Firmware and Interface. 

## Requirements

On Debian/Ubuntu:

Just do the following:

1. sudo apt-get install python graphviz

2. Test on bash : dot -V


3. sudo pip install gprof2dot

4. For the Beaglebone is also needed to be done

That's it

On Windows:

1. Download Graphviz from the link bellow:
https://bobswift.atlassian.net/wiki/pages/viewpageattachments.action?pageId=20971549&metadataLink=true

2. Then follow instruction 7-15 in the link below:
https://bobswift.atlassian.net/wiki/spaces/GVIZ/pages/20971549/How+to+install+Graphviz+software

3. Test on command line: dot -V

4. pip install gprof2dot 

5. As admin run: dot -c


## Command

You can visualize the .pstats file by the following command:

gprof2dot -f pstats output.pstats | dot -Tpng -o output.png










