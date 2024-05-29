#include <iostream>
#include "osm.h"
#include <sys/time.h>


/* Time measurement function for a simple arithmetic operation.
   returns time in nano-seconds upon success,
   and -1 upon failure.
   */
double osm_operation_time(unsigned int iterations) {
    struct timeval start, end;

    if (iterations == 0) {
        return -1;
    }

    if (iterations % 10 != 0) {
        iterations = iterations + 10 - iterations % 10;
    }
    iterations = iterations / 10;
    int x0 = 0;
    int x1 = 0;
    int x2 = 0;
    int x3 = 0;
    int x4 = 0;
    int x5 = 0;
    int x6 = 0;
    int x7 = 0;
    int x8 = 0;
    int x9 = 0;
    gettimeofday(&start, NULL);
    for (int i = 0; i < iterations; i++) {
        x0 = x0+1;
        x1 = x1+1;
        x2 = x2+1;
        x3 = x3+1;
        x4 = x4+1;
        x5 = x5+1;
        x6 = x6+1;
        x7 = x7+1;
        x8 = x8+1;
        x9 = x9+1;
    }
    gettimeofday(&end, NULL);


    return 1000 * ((double) 1000000 * (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec)) / (iterations * 10);
}


void empty_func() {}

/* Time measurement function for an empty function call.
   returns time in nano-seconds upon success,
   and -1 upon failure.
   */
double osm_function_time(unsigned int iterations) {
    struct timeval start, end;

    if (iterations == 0) {
        return -1;
    }

    if (iterations % 10 != 0) {
        iterations = iterations + 10 - iterations % 10;
    }
    iterations = iterations / 10;
    gettimeofday(&start, NULL);


    for (int i = 0; i < iterations; i++) {
        empty_func();
        empty_func();
        empty_func();
        empty_func();
        empty_func();
        empty_func();
        empty_func();
        empty_func();
        empty_func();
        empty_func();

    }
    gettimeofday(&end, NULL);


    return 1000 * ((double) 1000000 * (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec)) / (iterations * 10);
}


/* Time measurement function for an empty trap into the operating system.
   returns time in nano-seconds upon success,
   and -1 upon failure.
   */
double osm_syscall_time(unsigned int iterations) {
    struct timeval start, end;

    if (iterations == 0) {
        return -1;
    }

    if (iterations % 10 != 0) {
        iterations = iterations + 10 - iterations % 10;
    }
    iterations = iterations / 10;
    gettimeofday(&start, NULL);

    for (int i = 0; i < iterations; i++) {
        OSM_NULLSYSCALL;
        OSM_NULLSYSCALL;
        OSM_NULLSYSCALL;
        OSM_NULLSYSCALL;
        OSM_NULLSYSCALL;
        OSM_NULLSYSCALL;
        OSM_NULLSYSCALL;
        OSM_NULLSYSCALL;
        OSM_NULLSYSCALL;
        OSM_NULLSYSCALL;

    }
    gettimeofday(&end, NULL);

    return 1000 * ((double) 1000000 * (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec)) / (iterations * 10);
}

